from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'
S=json.loads((ROOT/'content/site.json').read_text())
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.links=[];self.ids=set();self.canonical=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  for key in ('href','src'):
   if key in a:self.links.append(a[key])
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
pages={p:Page(p.read_text()) for p in OUT.rglob('*.html') if not p.is_symlink()}
errors=[]
for p,page in pages.items():
 assert len(page.canonical)==1,p
 for href in page.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  path=unquote(u.path)
  target=p if not path else OUT/path.removeprefix(S['base_path']+'/') if path.startswith('/') else p.parent/path
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append((str(p),href))
  elif u.fragment and target in pages and u.fragment not in pages[target].ids:errors.append((str(p),href))
for p in (OUT/'journal').glob('*/index.html'):
 assert S['guide_url'].replace('&','&amp;') in p.read_text(),p
for f in ['sitemap.xml','feed.xml']:ET.parse(OUT/f)
assert not errors,errors
print(f'Validated {len(pages)} HTML pages, internal links, fragments, guide calls to action and XML feeds.')
