from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('shortener.urls')),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': settings.STATIC_ROOT}),
)
