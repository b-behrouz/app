#!/usr/bin/env python3
"""Build the existing main/root Pages source without allowing Jekyll to replace it with README."""
import argparse,json,re,html as html_module
from pathlib import Path
from build_preview import ROOT,render
MARKER='<!-- hamghadam-generated-route -->'
def expected_files(preview,app,config):
    base=config['base_path']
    if not re.fullmatch(r'/(?:[A-Za-z0-9_-]+/)*',base):raise ValueError('Invalid Pages base_path')
    # Center IDs belong to the embedded published directory, not guide section IDs.
    ids=list(dict.fromkeys(re.findall(r'"id":"([a-z0-9-]+)","phones":',app)))
    if not ids:raise ValueError('No center routes found; review the embedded directory schema')
    routes=['/need','/feedback','/introduce-center']+['/centers/'+value for value in ids]
    result={'index.html':preview,'.nojekyll':b''}
    for route in routes:
        destination=base+'#'+route
        body=(MARKER+'<!doctype html><html lang="fa-IR" dir="rtl"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<title>هم‌قدم</title><meta http-equiv="refresh" content="0;url='+html_module.escape(destination,quote=True)+'">'
          '<script>location.replace('+json.dumps(destination)+'+location.search);</script>'
          '</head><body><a href="'+html_module.escape(destination,quote=True)+'">بازکردن صفحه در هم‌قدم</a></body></html>')
        result[route.lstrip('/')+'/index.html']=body.encode()
    fallback=(MARKER+'<!doctype html><html lang="fa-IR" dir="rtl"><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1"><title>هم‌قدم</title>'
      '<script>const base='+json.dumps(base)+';if(location.protocol!=="file:"&&location.pathname.startsWith(base))'
      '{const route="/"+location.pathname.slice(base.length);location.replace(base+"#"+route+location.search);}'
      '</script><a href="'+html_module.escape(base)+'">خانهٔ هم‌قدم</a></html>')
    result['404.html']=fallback.encode()
    manifest={'base_path':base,'routes':routes,'files':sorted(result)}
    result['.pages-manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    return result

def files():
    preview=render()
    if (ROOT/'hamghadam-preview.html').read_bytes()!=preview:raise ValueError('Build the preview before building Pages')
    return expected_files(preview,(ROOT/'src/app.js').read_text(),json.loads((ROOT/'config/pages.json').read_text()))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    output=files()
    if args.check:
        for name,data in output.items():
            p=ROOT/name
            if not p.exists() or p.read_bytes()!=data:raise SystemExit('Stale Pages output: '+name)
        print('PASS: Pages root index, .nojekyll and all direct-entry routes match current sources.');return
    old=ROOT/'.pages-manifest.json'
    if old.exists():
        previous=json.loads(old.read_text()).get('files',[])
        for name in set(previous)-set(output):
            p=(ROOT/name).resolve()
            if not p.is_relative_to(ROOT):raise ValueError('Invalid previous generated output path')
            if p.exists() and p.is_file() and p.read_text().startswith(MARKER):p.unlink()
    for name,data in output.items():
        p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    print('Built Pages source at repository root:',len(output),'files; index.html is byte-identical to the local preview.')
if __name__=='__main__':main()
