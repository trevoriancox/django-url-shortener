import datetime

from django.db import models
from django.conf import settings

from shortener.baseconv import base62

class Link(models.Model):
    """
    Model that represents a shortened URL
    """
    url = models.URLField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=0)

    def to_base62(self):
        return base62.from_decimal(self.id)

    def short_url(self):
        return settings.SITE_BASE_URL + self.to_base62()

    def __unicode__(self):
        return  '%s : %s' % (self.to_base62(), self.url)

    class Meta:
        get_latest_by = 'date_submitted'
