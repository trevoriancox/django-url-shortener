import random
import string
import sys


from django.core.urlresolvers import reverse
from django.template import Context, RequestContext, Template
from django.test import TestCase
from django.test.client import Client, RequestFactory

from shortener.baseconv import base62, DecodingError, EncodingError
from shortener.forms import too_long_error
from shortener.models import Link

# needed for the short_url templatetag
CUSTOM_HTTP_HOST = 'django.testserver'


class TemplateTagTestCase(TestCase):
    def setUp(self):
        self.HTTP_HOST = CUSTOM_HTTP_HOST
        self.factory = RequestFactory(HTTP_HOST=self.HTTP_HOST)

    def test_short_url(self):
        """
        the short_url templatetag works with auto-generated links
        """
        link = Link.objects.create(url='http://www.python.org/')
        request = self.factory.get(reverse('index'))
        out = Template(
            "{% load shortener_helpers %}"
            "{% short_url link %}"
        ).render(RequestContext(request, {'link': link}))
        self.assertEqual(
            out, 'http://%s/%s' % (self.HTTP_HOST, link.to_base62()))

    def test_short_url_with_custom(self):
        """
        the short_url templatetag works with custom links
        """
        custom = 'python'
        link = Link.objects.create(
            url='http://www.python.org/', id=base62.to_decimal(custom))
        request = self.factory.get(reverse('index'))
        out = Template(
            "{% load shortener_helpers %}"
            "{% short_url link %}"
        ).render(RequestContext(request, {'link': link}))
        self.assertEqual(
            out, 'http://%s/%s' % (self.HTTP_HOST, link.to_base62()))


class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST=CUSTOM_HTTP_HOST)

    def test_submit(self):
        """
        submit view with auto-generated short url
        """
        url = u'http://www.python.org/'
        response = self.client.post(reverse('submit'), {'url': url})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_success.html')
        self.assertIn('link', response.context)
        link = response.context['link']
        self.assertIsInstance(link, Link)
        self.assertEqual(url, link.url)
        self.assertEqual(link.usage_count, 0)
        self.assertEqual(base62.from_decimal(link.id), link.to_base62())

    def test_submit_with_custom(self):
        """
        submit view with a custom short url
        """
        url = u'http://www.python.org/'
        custom = 'mylink'
        response = self.client.post(reverse('submit'), {
            'url': url, 'custom': custom})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_success.html')
        self.assertIn('link', response.context)
        link = response.context['link']
        self.assertIsInstance(link, Link)
        self.assertEqual(url, link.url)
        self.assertEqual(link.usage_count, 0)
        self.assertEqual(link.to_base62(), custom)

    def test_submit_with_bad_character_in_custom(self):
        """
        submit view with an invalid character in custom
        """
        url = u'http://www.python.org/'
        custom = 'my_link_bad_chars:##$#$%^$&%^**'
        response = self.client.post(reverse('submit'), {
            'url': url, 'custom': custom})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_failed.html')
        self.assertFormError(
            response, 'link_form', 'custom', u'Invalid character for encoding: _')
        self.assertNotIn('link', response.context)

    def test_submit_with_custom_no_repeats(self):
        """
        submitting a request w/a custom name fails if it is already taken
        """
        url = u'http://www.python.org/'
        custom = 'mylink'

        # first time should succeed
        response = self.client.post(reverse('submit'), {
            'url': url, 'custom': custom})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_success.html')
        self.assertIn('link', response.context)
        link = response.context['link']
        self.assertIsInstance(link, Link)
        self.assertEqual(url, link.url)
        self.assertEqual(link.usage_count, 0)
        self.assertEqual(link.to_base62(), custom)

        # second time should be an error
        response = self.client.post(reverse('submit'), {
            'url': url, 'custom': custom})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_failed.html')
        self.assertFormError(
            response, 'link_form', 'custom', '"%s" is already taken' % custom)
        self.assertNotIn('link', response.context)

    def test_submit_long_custom(self):
        """
        if a custom shortened url is too long we return an error
        """
        url = u'http://www.python.org/'
        custom = 'MyLinkCustomLinkThatIsTooLongOoooooooohYea'
        response = self.client.post(reverse('submit'), {
            'url': url, 'custom': custom})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_failed.html')
        self.assertFormError(response, 'link_form', 'custom', too_long_error)

    def test_follow(self):
        """
        the follow view on a valid url
        """
        url = 'http://www.python.org/'
        link = Link.objects.create(url=url)
        self.assertEqual(link.usage_count, 0)

        # follow the short url and get a redirect
        response = self.client.get(reverse('follow', kwargs={
            'base62_id': link.to_base62()}))
        self.assertRedirects(response, url, 301)

        # re-fetch link so that we can make sure that usage_count incremented
        link = Link.objects.get(id=link.id)
        self.assertEqual(link.usage_count, 1)

    def test_follow_404(self):
        """
        follow on an unknown url should return 404
        """
        url = u'http://www.python.org/'
        response = self.client.get(reverse('follow', kwargs={
            'base62_id': "fails"}))
        self.assertEqual(response.status_code, 404)

    def test_info(self):
        """
        the info view on a valid url
        """
        url = u'http://www.python.org/'
        link = Link.objects.create(url=url)
        response = self.client.get(reverse('info', kwargs={
            'base62_id': link.to_base62()}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/link_info.html')

    def test_info_404(self):
        """
        info on an unknown url should return 404
        """
        url = u'http://www.python.org/'
        response = self.client.get(reverse('info', kwargs={
            'base62_id': "fails"}))
        self.assertEqual(response.status_code, 404)


class LinkTestCase(TestCase):
    def test_create(self):
        """
        Link.base_62() is derived from auto-generated Link.id
        """
        link = Link.objects.create(url='http://www.python.org')
        self.assertEqual(link.to_base62(), base62.from_decimal(link.id))

    def test_create_with_custom_id(self):
        """
        Link.base_62() is derived from custom Link.id
        """
        id = 5000
        link = Link.objects.create(id=id, url='http://www.python.org')
        self.assertEqual(link.to_base62(), base62.from_decimal(id))


class BaseconvTestCase(TestCase):
    def test_symmetry_int(self):
        """
        symmetry for encoding/decoding values
        """
        for x in xrange(1000):
            random_int = random.randint(0, sys.maxint)
            encoded_int = base62.from_decimal(random_int)
            self.assertEqual(random_int, base62.to_decimal(encoded_int))

    def test_encoding_non_int_fails(self):
        """
        calling from_decimal() on letters raises an EncodingError
        """
        self.assertRaises(EncodingError, base62.from_decimal, string.letters)

    def test_decoding_non_str_fails(self):
        """
        decoding a non-str should fail with DecodingError
        """
        self.assertRaises(DecodingError, base62.to_decimal, sys.maxint)

    def test_illgal_character(self):
        """
        trying to encode a character that is not within base62 raises an
        EncodingError
        """
        self.assertRaises(DecodingError, base62.to_decimal, '@@@@')
