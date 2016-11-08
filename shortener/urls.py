try:
    from django.conf.urls import patterns, url
except:
    # Django <=1.5
    from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('shortener.views',
    url(r'^$', 'index', name='index'),
    url(r'^info/(?P<base62_id>\w+)$', 'info', name='info'),
    url(r'^submit/$', 'submit', name='submit'),
    url(r'^(?P<base62_id>\w+)$', 'follow', name='follow'),
)
