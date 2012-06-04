import random
import string
import sys


from django.core.urlresolvers import reverse
from django.test import TestCase

from shortener.baseconv import base62, DecodingError, EncodingError
from shortener.models import Link


class ViewTestCase(TestCase):
    def test_submit(self):
        url = u'http://www.python.org/'
        response = self.client.post(reverse('submit'), {'url': url,})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_success.html')
        self.assertIn('link', response.context)
        link = response.context['link']
        self.assertIsInstance(link, Link)
        self.assertEqual(url, link.url)
        self.assertEqual(link.usage_count, 0)
        self.assertEqual(base62.from_decimal(link.id), link.to_base62())

    def test_submit_with_custom(self):
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
        Submit with an invalid character in custom
        """
        url = u'http://www.python.org/'
        custom = 'my_link_bad_chars:##$#$%^$&%^**'
        response = self.client.post(reverse('submit'), {
            'url': url, 'custom': custom})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_failed.html')
        self.assertFormError(response, 'link_form', 'custom', 'Invalid character: "_"')
        self.assertNotIn('link', response.context)

    def test_submit_with_custom_no_repeats(self):
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
        self.assertFormError(response, 'link_form', 'custom', '"%s" is already taken' % custom)

        self.assertNotIn('link', response.context)

    def test_follow(self):
        url = u'http://www.python.org/'
        response = self.client.post(reverse('submit'), {'url': url,})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shortener/submit_success.html')

        link = response.context['link']
        self.assertIsInstance(link, Link)
        self.assertEqual(url, link.url)
        self.assertEqual(base62.from_decimal(link.id), link.to_base62())
        self.assertEqual(link.usage_count, 0)

        # follow the short url and get a redirect
        response = self.client.get(link.short_url())
        self.assertRedirects(response, url, 301)

        # re-fetch link so that we can make sure that usage_count incremented
        link = Link.objects.get(id=link.id)
        self.assertEqual(link.usage_count, 1)


class LinkTestCase(TestCase):
    def test_create(self):
        link = Link.objects.create(url='http://www.python.org')

        # verify that link.short_url() is derived from link.id and that
        # the short_url() ends with the base_62() encoding of link.id
        self.assertEqual(link.to_base62(), base62.from_decimal(link.id))
        self.assertTrue(link.short_url().endswith(link.to_base62()))

    def test_create_with_custom_id(self):
        """
        Create a shortened URL with non-default id specified
        """
        id = 5000
        link = Link.objects.create(id=id, url='http://www.python.org')
        self.assertEqual(link.to_base62(), base62.from_decimal(id))
        self.assertTrue(link.short_url().endswith(link.to_base62()))


class BaseconvTestCase(TestCase):
    def test_symmetry_int(self):
        random_int = random.randint(0, sys.maxint)
        encoded_int = base62.from_decimal(random_int)
        self.assertEqual(random_int, base62.to_decimal(encoded_int))

    def test_encoding_non_int_fails(self):
        try:
            encoding = base62.from_decimal(string.letters)
        except EncodingError, e:
            err = e
        self.assertIsInstance(err, EncodingError)

    def test_decoding_non_str_fails(self):
        try:
            decoding = base62.to_decimal(sys.maxint)
        except DecodingError, e:
            err = e
        self.assertIsInstance(err, DecodingError)
