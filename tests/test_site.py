"""Static website regressions; these do not substitute for browser testing."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.links=[];self.labels=[];self.scripts=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a':self.links.append(attrs['href'])
        if tag=='script' and 'src' in attrs:self.scripts.append(attrs['src'])
        if 'aria-labelledby' in attrs:self.labels+=attrs['aria-labelledby'].split()
class SiteTests(unittest.TestCase):
    def test_links_and_labels(self):
        for name in ('index.html','shop.html'):
            page=Page((ROOT/name).read_text())
            self.assertEqual(len(page.ids),len(set(page.ids)))
            self.assertTrue(set(page.labels)<=set(page.ids))
            for href in page.links:
                u=urlsplit(href)
                if u.scheme or u.netloc:continue
                p=ROOT/unquote(u.path) if u.path else ROOT/name
                if p.is_dir():p=p/'index.html'
                self.assertTrue(p.exists(),href)
                if u.fragment:self.assertIn(u.fragment,Page(p.read_text()).ids)
    def test_shared_assistant_and_no_public_backend_default(self):
        for name in ('index.html','shop.html'):
            page=Page((ROOT/name).read_text())
            self.assertEqual(sum(urlsplit(src).path=='assistant.js' for src in page.scripts),1)
            self.assertEqual(page.scripts.count('assistant-config.js'),1)
        self.assertIn("window.GHINOVA_ASSISTANT_API = '';",(ROOT/'assistant-config.js').read_text())
        self.assertNotIn('MODEL_API_KEY',(ROOT/'assistant.js').read_text())
    def test_launcher_available_without_javascript(self):
        for name in ('index.html','shop.html'):
            text=(ROOT/name).read_text()
            launcher=re.search(r'<a id="ghinova-ai-launcher"[^>]*>.*?</a>',text)[0]
            self.assertIn('href="index.html#assistant"',launcher)
            self.assertIn('position:fixed',launcher)
            self.assertIn('Ghinova AI',launcher)
            self.assertEqual(text.count('id="ghinova-ai-launcher"'),1)
            self.assertIn('visual.css?v=launcher-2',text)
            self.assertIn('assistant.js?v=launcher-2',text)
    def test_shop_status_and_structured_data(self):
        text=(ROOT/'shop.html').read_text()
        graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
        offers=[r['offers']['price'] for r in graph['@graph'] if 'offers' in r]
        self.assertEqual(sorted(offers),[5,9,15,59])
        self.assertEqual(text.count('class="product-status">Coming Soon'),8)
        self.assertEqual(text.count('class="agent-card"'),4)
        for body in re.findall(r'<article class="agent-card".*?</article>',text,re.S):
            self.assertNotIn('whop.com',body)
            self.assertIn('Planned',body)
if __name__=='__main__':unittest.main()
