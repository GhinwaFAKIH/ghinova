"""Build the assistant's factual catalog only from checked-in website content."""
import json
import re
from pathlib import Path
from html import unescape
ROOT = Path(__file__).resolve().parent.parent

def plain(text):
    return unescape(re.sub('<[^>]+>', '', text)).strip()

def build():
    shop = (ROOT / 'shop.html').read_text()
    home = (ROOT / 'index.html').read_text()
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', shop, re.S)[1])['@graph']
    rows = []
    for item in graph:
        if item['@type'] not in ('Course', 'LearningResource'):
            continue
        slug = item['@id'].split('#')[-1]
        row = dict(id=slug, name=item['name'], description=item['description'], status='listed', level=item['educationalLevel'], url='shop.html#'+slug, source='shop.html')
        if 'offers' in item:
            row.update(price=item['offers']['price'], checkout=item['offers']['url'])
        elif item.get('isAccessibleForFree'):
            row.update(price=0, download=item['encoding']['contentUrl'].split('/ghinova/')[-1])
            assert (ROOT / row['download']).is_file()
        rows.append(row)
    for slug, body in re.findall(r'<li class="tier-product" id="([^"]+)">(.*?)</li>', shop, re.S):
        if 'Coming Soon' in body:
            rows.append(dict(id=slug, name=plain(re.search('<h3>(.*?)</h3>',body,re.S)[1]), description=plain(re.search('<p>(.*?)</p>',body,re.S)[1]), status='coming_soon', price=0 if slug=='introduction-to-ai' else None, url='shop.html#'+slug, source='shop.html'))
    for slug, body in re.findall(r'<article class="agent-card" id="([^"]+)".*?>(.*?)</article>',shop,re.S):
        rows.append(dict(id=slug, name=plain(re.search('<h3[^>]*>(.*?)</h3>',body,re.S)[1]), description=plain(re.search('<p>(.*?)</p>',body,re.S)[1]), status='planned_service', price=None, url='shop.html#'+slug, contact='index.html#contact', source='shop.html'))
    for slug, price, name, link in [('training-1h',20,'1-hour private training','ghinova-1-to-1-training-session'),('training-5h',90,'5-hour private training package','5-hour-package'),('training-10h',170,'10-hour private training package','10-hour-package')]:
        url='https://cal.com/ginwa-fakih-fluyzt/'+link
        assert url in home and '€'+str(price) in home
        rows.append(dict(id=slug,name=name,description='Live Python or AI training. Prices before applicable tax.',status='listed',price=price,url='index.html#book',checkout=url,source='index.html'))
    for slug, name, path in [('pdf-tutorial','Free Python PDF chatbot tutorial','guides/pdf-chatbot-python/'),('rag-tutorial','Free RAG evaluation tutorial','guides/evaluate-rag-chatbot-python/')]:
        assert (ROOT/path/'index.html').exists() and path in shop
        rows.append(dict(id=slug,name=name,description='A free written Python guide.',status='listed',price=0,url=path,source=path+'index.html'))
    rows.extend([
        dict(id='contact',name='Contact Ginwa',description='Discuss training or request a custom project quote.',status='contact',price=None,url='index.html#contact',source='index.html'),
        dict(id='level-two',name='Level 2: LLMs, RAG and GraphRAG',description='Planned self-paced course. No confirmed price or checkout.',status='coming_soon',price=None,url='index.html#level-two',source='index.html')
    ])
    assert len({x['id'] for x in rows})==len(rows)
    return rows

if __name__=='__main__':
    target=Path(__file__).with_name('catalog.json')
    target.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n')
    print('Wrote',len(build()),'source-verified catalog entries.')
