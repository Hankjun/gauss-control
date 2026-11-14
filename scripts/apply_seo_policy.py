"""Publish canonical metadata and the sitemap for reviewed public pages."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
import argparse
import json
import re
import xml.etree.ElementTree as ET

PRIMARY = 'https://www.gauss-control.net'
PREVIOUS_ORIGINS = (
    'https://gauss-control-process-intelligence.zaqprmhm56595.chatgpt.site',
    'https://hankjun.github.io/gauss-control',
    'http://www.gauss-control.net',
)
INDEXABLE = {'/', '/about/', '/applications/', '/contact/', '/services/',
             '/processes/', '/products/', '/products/videos/', '/knowledge/',
             '/applications/automotive/', '/applications/aerospace/',
             '/applications/wind-energy/', '/applications/wire-tube/',
             '/applications/semiconductors/'}
LANGUAGES = {'en': '', 'zh-CN': '/zh', 'es': '/es'}
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XHTML = 'http://www.w3.org/1999/xhtml'
ET.register_namespace('', NS)
ET.register_namespace('xhtml', XHTML)

def page_route(relative):
    value = '/' + relative.as_posix()
    return value[:-len('index.html')] if value.endswith('/index.html') else value

def base_route(route):
    for prefix in ('/zh/', '/es/'):
        if route.startswith(prefix):
            return '/' + route[len(prefix):]
    return route

def html_meta(text, name, content):
    pattern = r'<meta\b(?=[^>]*\bname=[\"\']' + re.escape(name) + r'[\"\'])[^>]*>'
    value = '<meta name="' + name + '" content="' + content + '">'
    if re.search(pattern, text, re.I):
        return re.sub(pattern, lambda _: value, text, flags=re.I)
    return text.replace('</head>', value + '</head>', 1)

def enrich_metadata(text, route):
    url = PRIMARY + route
    text = re.sub(r'<meta property="og:url" content="[^"]*">', '', text)
    text = text.replace('</head>', f'<meta property="og:url" content="{url}"></head>', 1)
    base = base_route(route)
    language = 'zh-CN' if route.startswith('/zh/') else 'es' if route.startswith('/es/') else 'en'
    if base == '/':
        def enrich_organization(match):
            schemas = json.loads(match[1])
            for entity in schemas:
                if entity.get('@type') == 'Organization':
                    entity.update({
                        '@id': PRIMARY + '/#organization',
                        'address': {
                            '@type': 'PostalAddress', 'streetAddress': 'No. 2 Taiyun Road',
                            'addressLocality': 'Wuxi', 'addressRegion': 'Jiangsu', 'addressCountry': 'CN',
                        },
                        'sameAs': ['https://www.youtube.com/@gausscontrol2023'],
                    })
            return '<script type="application/ld+json">' + json.dumps(schemas).replace('</', '<\\/') + '</script>'

        return re.sub(r'<script type="application/ld\+json">(.*?)</script>', enrich_organization, text, count=1, flags=re.S)
    if base in INDEXABLE and base.startswith('/applications/') and base != '/applications/':
        # Use the visible localized heading and the page description.
        heading = unescape(re.search(r'<h1>(.*?)</h1>', text, re.S)[1])
        description = unescape(re.search(r'<meta name="description" content="([^"]*)">', text)[1])
        schema = {
            '@context': 'https://schema.org', '@type': 'WebPage', '@id': url + '#webpage',
            'url': url, 'name': heading, 'description': description, 'inLanguage': language,
            'publisher': {'@id': PRIMARY + '/#organization'},
        }
        script = '<script type="application/ld+json" id="industry-webpage">' + json.dumps(schema).replace('</', '<\\/') + '</script>'
        text = re.sub(r'<script type="application/ld\+json" id="industry-webpage">.*?</script>', '', text, flags=re.S)
        return text.replace('</head>', script + '</head>', 1)
    return text

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = []
        self.canonical = []
        self.alternates = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name') == 'robots':
            self.robots.append(attrs.get('content'))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href'))
        if tag == 'link' and attrs.get('hreflang'):
            self.alternates[attrs['hreflang']] = attrs.get('href')

def apply(root, mode):
    root = Path(root)
    expected = {PRIMARY + prefix + route for route in INDEXABLE for prefix in LANGUAGES.values()}
    actual = set()
    pages = list(root.rglob('*.html'))
    for path in pages:
        route = page_route(path.relative_to(root))
        eligible = mode == 'primary' and base_route(route) in INDEXABLE
        text = path.read_text()
        for origin in PREVIOUS_ORIGINS:
            text = text.replace(origin, PRIMARY)
        text = html_meta(text, 'robots', 'index, follow' if eligible else 'noindex, follow')
        canonical = '<link rel="canonical" href="' + PRIMARY + route + '">'
        text = re.sub(r'<link\b(?=[^>]*\brel=[\"\']canonical[\"\'])[^>]*>', lambda _: canonical, text, flags=re.I)
        if base_route(route) in INDEXABLE:
            text = enrich_metadata(text, route)
        if path.name == '404.html':
            text = re.sub(r'<link\b(?=[^>]*\bhreflang=)[^>]*>', '', text, flags=re.I)
        path.write_text(text)
        meta = Metadata()
        meta.feed(text)
        assert meta.robots == [('index, follow' if eligible else 'noindex, follow')], path
        assert meta.canonical == [PRIMARY + route], path
        if eligible:
            actual.add(PRIMARY + route)
            base = base_route(route)
            for code, prefix in LANGUAGES.items():
                assert meta.alternates.get(code) == PRIMARY + prefix + base, (path, code)
            assert meta.alternates.get('x-default') == PRIMARY + base, path
    if mode == 'primary':
        assert actual == expected, {'missing': sorted(expected - actual), 'extra': sorted(actual - expected)}
    else:
        assert not actual
    urls = ET.Element('{' + NS + '}urlset')
    for route in sorted(INDEXABLE) if mode == 'primary' else []:
        for _, prefix in LANGUAGES.items():
            node = ET.SubElement(urls, '{' + NS + '}url')
            ET.SubElement(node, '{' + NS + '}loc').text = PRIMARY + prefix + route
            for code, alternate_prefix in LANGUAGES.items():
                ET.SubElement(node, '{' + XHTML + '}link', {'rel': 'alternate', 'hreflang': code, 'href': PRIMARY + alternate_prefix + route})
            ET.SubElement(node, '{' + XHTML + '}link', {'rel': 'alternate', 'hreflang': 'x-default', 'href': PRIMARY + route})
    ET.ElementTree(urls).write(root / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    robots = 'User-agent: *\nAllow: /\n'
    if mode == 'primary':
        robots += '\nSitemap: ' + PRIMARY + '/sitemap.xml\n'
    else:
        robots += '\n# Secondary publication. Pages use noindex and canonical URLs on ' + PRIMARY + '/\n'
    (root / 'robots.txt').write_text(robots)
    locs = {n.text for n in ET.parse(root / 'sitemap.xml').findall('.//{' + NS + '}loc')}
    assert locs == actual
    print(f'{mode}: verified {len(pages)} HTML files; {len(actual)} indexable URLs; sitemap matches policy.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--mode', choices=('primary', 'mirror'), required=True)
    args = parser.parse_args()
    apply(args.root, args.mode)
