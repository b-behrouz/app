#!/usr/bin/env python3
"""Build only static production files; keep GitHub Pages and local preview unchanged."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
from build_preview import ROOT
from build_pages import expected_files, public_records, SITE
from site_assets import externalize
from production_pages import build_entries

def build(revision=None, output=None, skip_prerender=False):
    def read(name):
        return subprocess.check_output(['git','show',revision+':'+name],cwd=ROOT) if revision else (ROOT/name).read_bytes()
    raw=read('hamghadam-preview.html')
    app=read('src/app.js').decode()
    # Rollback of pre-migration revisions must retain their inline assets and domain.
    legacy=bool(revision and b'https://rahnamasalamat.ir/' not in raw)
    if legacy:
        old=json.loads(read('.pages-manifest.json'))
        files={'index.html':raw}
        for name in old['files']:
            if name.endswith('.html') and name!='index.html':
                files[name]=read(name).replace(b'/app/#',b'/#').replace(b'base="/app/"',b'base="/"')
    else:
        preview,assets=externalize(raw.decode())
        snapshots=None
        if not skip_prerender:
            captured=json.loads(read('data/prerender/pages.json'))
            if captured['source_sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Prerender is stale. Build a seed and run scripts/prerender.cjs first.')
            snapshots=captured['pages']
        files=build_entries(preview.encode(),app,snapshots)
        files.update(assets)
        files['og-image.png']=read('assets/brand/og-image.png')
        from xml.sax.saxutils import escape
        urls=[SITE,SITE+'about/',SITE+'categories/hospitals/',SITE+'categories/pharmacies/']+[SITE+'centers/'+r['id']+'/' for r in public_records(app)]
        files['sitemap.xml']=('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(url)+'</loc></url>' for url in urls)+'</urlset>\n').encode()
        files['robots.txt']=('User-agent: *\nAllow: /\nSitemap: '+SITE+'sitemap.xml\n').encode()
    assert 'index.html' in files and all(not name.startswith('.') for name in files)
    total=sum(map(len,files.values()))
    if total > 15*1024*1024:raise ValueError('Production bundle exceeds 15 MiB budget')
    manifest={'schema':1,'revision':revision or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'prerendered':bool(not legacy and not skip_prerender),
              'files':{name:hashlib.sha256(data).hexdigest() for name,data in files.items()},'bytes':total}
    files['.hamghadam-deploy.json']=(json.dumps(manifest,sort_keys=True)+'\n').encode()
    if output:
        output=Path(output)
        if output.exists() and any(output.iterdir()):raise ValueError('Use a fresh output directory')
        for name,data in files.items():
            p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            # cPanel ZIP extraction preserves these modes. A restrictive build
            # umask must not leave public assets unreadable to the web server.
            p.chmod(0o644)
        output.chmod(0o755)
        for directory in output.rglob('*'):
            if directory.is_dir(): directory.chmod(0o755)
    return files
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--revision');parser.add_argument('--skip-prerender',action='store_true',help='Local seed only, never deploy this output');parser.add_argument('--output',required=True);args=parser.parse_args()
    result=build(args.revision,args.output,args.skip_prerender);print('Production:',len(result),'files,',sum(map(len,result.values())),'bytes; base path /')
