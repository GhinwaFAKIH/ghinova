"""Build a public-only Render artifact; never edit the GitHub Pages sources."""
import json
import os
import shutil
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
FILES=['index.html','shop.html','style.css','visual.css','script.js','assistant.js','assistant-config.js','ghinwa-avatar.png','googled67fe137e84fdf4a.html','sitemap.xml']
DIRS=['guides','workshops','course-labs']
def build(destination=None,api_url=None):
    destination=Path(destination or ROOT/'dist')
    api_url=os.getenv('PUBLIC_API_URL','') if api_url is None else api_url
    if api_url:
        u=urlsplit(api_url)
        if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path!='/api/chat':raise ValueError('PUBLIC_API_URL must be an HTTPS /api/chat endpoint')
    if destination.resolve()==ROOT:raise ValueError('Cannot overwrite source tree')
    # Only our dedicated default build directory may be automatically replaced.
    if destination.exists():
        if destination.resolve()!=ROOT/'dist':raise ValueError('Custom destination must not exist')
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for name in FILES:shutil.copy2(ROOT/name,destination/name)
    for name in DIRS:
        for source in (ROOT/name).rglob('*'):
            if source.is_file() and source.suffix in ('.html','.css','.js','.ipynb','.pdf','.png','.jpg','.svg'):
                target=destination/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    (destination/'assistant-config.js').write_text('// Public build configuration. No credentials.\nwindow.GHINOVA_ASSISTANT_API = '+json.dumps(api_url)+';\n')
    return destination
if __name__=='__main__':print('Static artifact:',build())
