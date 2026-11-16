#!/usr/bin/env python3
"""Build the existing main/root Pages source without allowing Jekyll to replace it with README."""
import argparse,json,re,html as html_module
from pathlib import Path
from build_preview import ROOT,render
MARKER='<!-- hamghadam-generated-route -->'
SITE='https://rahnamasalamat.ir/'
def public_records(app):
    care=json.loads(re.search(r'var ld=JSON.parse\(`(.*?)`\)',app,re.S).group(1))
    medical=json.loads(re.search(r'^const HAMGHADAM_MEDICAL_DATA = (.*);',app).group(1))['records']
    return care+medical

def route_metadata(app, route):
    """Reuse brand and route copy from the runtime for generated entry HTML."""
    brand_source=re.search(r'var Wm=\{(.*?)\};function Gm',app,re.S).group(1)
    brand=dict(re.findall(r'(\w+):`([^`]*)`',brand_source))
    seo_source=re.search(r'qx=\{(.*?)\};function Jx',app,re.S).group(1)
    seo=dict(re.findall(r'(\w+):`([^`]*)`',seo_source))
    route_source=app.split('function Jx(',1)[1].split('var Yx=',1)[0]
    titles=dict(re.findall(r"'([^']+)':'([^']*)'",route_source.split('const titles=',1)[1].split(';',1)[0]))
    descriptions=dict(re.findall(r"'([^']+)':'([^']*)'",route_source.split('const descriptions=',1)[1].split('};',1)[0]))
    care_match=re.search(r'var ld=JSON.parse\(`(.*?)`\)',app,re.S)
    records=json.loads(care_match.group(1)) if care_match else []
    medical_match=re.search(r'^const HAMGHADAM_MEDICAL_DATA = (.*);',app)
    if medical_match:records+=json.loads(medical_match.group(1))['records']
    record=next((r for r in records if route=='/centers/'+r['id']),None)
    if record:
        label=record.get('fullName') or record['name']
        services=record.get('services') if record.get('type') else record.get('details',{}).get('services',[])
        description='؛ '.join(str(v) for v in [label,record.get('address'),*(services or [])] if v)[:300]
    elif route=='/404':
        label='صفحه پیدا نشد';description='از فهرست خدمات سلامت، بیمارستان‌ها، داروخانه‌ها و مراکز مراقبت در راهنمای سلامت ادامه دهید.'
    else:label=titles.get(route);description=descriptions.get(route,seo['description'])
    return {'title':label+' | '+brand['name'] if label else seo['title'],'description':description,'name':brand['name'],'canonical':SITE+(route.strip('/')+'/' if route not in ['/', '/404'] else ''),'notfound':route=='/404','indexable':route=='/about' or bool(record) or route=='/'}

def entry_meta(app,route):
    data=route_metadata(app,route)
    esc=lambda value:html_module.escape(value,quote=True)
    markup=('<title>'+esc(data['title'])+'</title>'
      '<meta name="description" content="'+esc(data['description'])+'">'
      '<link rel="canonical" href="'+esc(data['canonical'])+'">'
      '<meta property="og:url" content="'+esc(data['canonical'])+'">'
      '<meta name="twitter:url" content="'+esc(data['canonical'])+'">'
      '<meta property="og:image" content="'+SITE+'og-image.png">'
      '<meta name="twitter:image" content="'+SITE+'og-image.png">'
      '<meta name="twitter:card" content="summary_large_image">'
      '<meta name="robots" content="'+('index,follow' if data['indexable'] else 'noindex,follow')+'">'
      '<meta name="application-name" content="'+esc(data['name'])+'">'
      '<meta property="og:site_name" content="'+esc(data['name'])+'">'
      '<meta property="og:title" content="'+esc(data['title'])+'">'
      '<meta property="og:description" content="'+esc(data['description'])+'">'
      '<meta name="twitter:title" content="'+esc(data['title'])+'">'
      '<meta name="twitter:description" content="'+esc(data['description'])+'">')
    if data.get('notfound'):markup=re.sub(r'<link rel="canonical"[^>]*>|<meta (?:property|name)="(?:og:url|twitter:url)"[^>]*>','',markup)
    return markup

def expected_files(preview,app,config):
    base=config['base_path']
    if not re.fullmatch(r'/(?:[A-Za-z0-9_-]+/)*',base):raise ValueError('Invalid Pages base_path')
    ids=[r['id'] for r in public_records(app)]
    routes=['/about','/need','/feedback','/introduce-center','/family-need']+['/centers/'+value for value in ids]
    result={'index.html':preview,'.nojekyll':b''}
    for route in routes:
        destination=base+'#'+route
        body=(MARKER+'<!doctype html><html lang="fa-IR" dir="rtl"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          +entry_meta(app,route)
          +'<script>location.replace('+json.dumps(destination)+'+location.search);</script>'
          '</head><body><a href="'+html_module.escape(destination,quote=True)+'">بازکردن صفحه در راهنمای سلامت</a></body></html>')
        result[route.lstrip('/')+'/index.html']=body.encode()
    fallback=(MARKER+'<!doctype html><html lang="fa-IR" dir="rtl"><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'+entry_meta(app,'/404')
      +'<script>const base='+json.dumps(base)+';if(location.protocol!=="file:"&&location.pathname.startsWith(base))'
      '{const route="/"+location.pathname.slice(base.length);location.replace(base+"#"+route+location.search);}'
      '</script><a href="'+html_module.escape(base)+'">خانهٔ راهنمای سلامت</a></html>')
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
