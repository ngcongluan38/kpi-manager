from urllib.parse import urljoin
from django.conf import settings


def build_absolute_url(path, https=not settings.DEBUG):
    root = 'https://{}/'.format(settings.SITE_DOMAIN) if https else 'http://{}/'.format(settings.SITE_DOMAIN)
    return urljoin(root, path)
