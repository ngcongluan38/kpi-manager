from urllib.parse import urlsplit
import re

from lxml.html.clean import Cleaner, autolink_html
import lxml.html


WEBSITE_WHITELIST = [
    'youtube.com',
    'www.youtube.com',
    'youtu.be',
]


class NewCleaner(Cleaner):
    def allow_embedded_url(self, el, url):
        if self.whitelist_tags is not None and el.tag not in self.whitelist_tags:
            return False
        scheme, netloc, path, query, fragment = urlsplit(url)
        netloc = netloc.lower().split(':', 1)[0]
        if scheme not in ('http', 'https', ''):
            return False
        if netloc in self.host_whitelist:
            return True
        return False


cleaner = NewCleaner(
    page_structure=False,
    links=False,
    style=True,
    safe_attrs_only=False,
    embedded=True,
    host_whitelist=WEBSITE_WHITELIST,
    whitelist_tags=('iframe',),
    remove_tags=('html', 'head', 'body'),
    add_nofollow=True,
)

_link_regexes = [re.compile(
        r'(?P<body>https?://(?P<host>[a-z0-9._-]+)(?:/[/\-_.,a-z0-9ốẽỷăãđýỵẻưỡầéừơẩủớỉặậờàệỗễồụểẫũạằẵỳấíỹửìôứởẹộùêếịèẳáắềĩọổâợữảúự%&?;=~:@#+]*)?(?:\([/\-_.,a-z0-9ốẽỷăãđýỵẻưỡầéừơẩủớỉặậờàệỗễồụểẫũạằẵỳấíỹửìôứởẹộùêếịèẳáắềĩọổâợữảúự%&?;=~:@#+]*\))?)',
        re.I)]


def clean_up_html(html, method='html'):
    html = autolink_html(html, link_regexes=_link_regexes)
    html = lxml.html.fromstring(cleaner.clean_html(html))
    for h1 in html.findall('h1'):
        h1.tag = 'h2'
    for a in html.cssselect('a'):
        a.attrib['target'] = '_blank'
    return lxml.html.tostring(html, encoding='utf-8', method=method)