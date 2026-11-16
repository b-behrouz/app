"""Crawlable static entries sharing the unchanged application and style assets."""
import hashlib,re,html as html_module
from build_pages import SITE,public_records,route_metadata

def category_metadata(app,category):
    data=route_metadata(app,'/');data=dict(data)
    labels={'hospitals':'بیمارستان‌ها','pharmacies':'داروخانه‌ها'}
    data.update(title=labels[category]+' در مشهد | '+data['name'],canonical=SITE+'categories/'+category+'/')
    data['description']='نام، نشانی و راه‌های ارتباطی '+labels[category]+' در مشهد؛ پیش از مراجعه تلفنی بررسی کنید.'
    data['indexable']=True
    return data

def metadata_html(page,data):
    esc=lambda x:html_module.escape(x,quote=True)
    values={'description':data['description'],'og:title':data['title'],'twitter:title':data['title'],'og:description':data['description'],'twitter:description':data['description'],'og:url':data['canonical'],'twitter:url':data['canonical'],'robots':'index,follow' if data['indexable'] else 'noindex,follow'}
    page=re.sub(r'<title>.*?</title>','<title>'+esc(data['title'])+'</title>',page,flags=re.S)
    def meta(m):
        tag=m.group();key=re.search(r'(?:name|property)="([^"]+)"',tag)
        if key and key[1] in values:return re.sub(r'content="[^"]*"',lambda _: 'content="'+esc(values[key[1]])+'"',tag)
        return tag
    page=re.sub(r'<meta\b[^>]*>',meta,page)
    page=re.sub(r'<link rel="canonical" href="[^"]*"[^>]*>',lambda _: '<link rel="canonical" href="'+esc(data['canonical'])+'"/>',page)
    if data.get('notfound'):page=re.sub(r'<link rel="canonical"[^>]*>|<meta (?:property|name)="(?:og:url|twitter:url)"[^>]*>','',page)
    return page

def build_entries(preview,app,snapshots=None):
    assets={}
    def asset(kind,ext,body):
        raw=body.encode();name='assets/runtime/'+kind+'-'+hashlib.sha256(raw).hexdigest()[:24]+'.'+ext;assets[name]=raw;return '/'+name
    page=preview.decode()
    module=re.search(r'<script type="module">(.*?)</script>',page,re.S)
    js=asset('app','js',module[1]);page=page[:module.start()]+'<script type="module" data-app-runtime src="'+js+'"></script>'+page[module.end():]
    styles=re.findall(r'<style\b(?![^>]*id="rahnama-boot-style")[^>]*>(.*?)</style>',page,re.S);css=asset('styles','css','\n'.join(styles));first=True
    def style(_):
        nonlocal first
        if first:first=False;return '<link rel="stylesheet" href="'+css+'"/>'
        return ''
    page=re.sub(r'<style\b(?![^>]*id="rahnama-boot-style")[^>]*>.*?</style>',style,page,flags=re.S)
    page=page.replace('<html ', '<html data-routing="browser" ',1)
    # Convert old shared hash links without a network redirect; normal entries keep their real URL.
    boot='<script>if(location.hash.startsWith("#/"))history.replaceState(history.state,"",location.hash.slice(1));const p=new URLSearchParams(location.search);if(/^\\/categories\\/nurses\\/?$/.test(location.pathname)||(location.pathname==="/"&&p.get("category")==="nurses")){p.delete("category");history.replaceState(history.state,"","/"+(p.size?"?"+p.toString():""))}else if(location.pathname==="/"){const c=p.get("category");if(["hospitals","pharmacies"].includes(c)){p.delete("category");history.replaceState(history.state,"","/categories/"+c+"/"+(p.size?"?"+p.toString():""))}}</script>'
    page=page.replace('<script type="module"',boot+'<script type="module"',1)
    routes=['/','/about','/need','/feedback','/introduce-center','/family-need']+['/centers/'+r['id'] for r in public_records(app)]
    files=dict(assets)
    for route in routes:
        name='index.html' if route=='/' else route.strip('/')+'/index.html'
        files[name]=metadata_html(page,route_metadata(app,route)).encode()
    files['404.html']=metadata_html(page,route_metadata(app,'/404')).encode()
    for category in ['hospitals','pharmacies']:
        files['categories/'+category+'/index.html']=metadata_html(page,category_metadata(app,category)).encode()
    # Compatibility endpoint only: it is not a category and has no category content.
    files['categories/nurses/index.html']=('<!doctype html><html lang="fa-IR" dir="rtl"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="'+SITE+'"><meta http-equiv="refresh" content="0;url=/"><script>location.replace("/")</script></head><body><a href="/">صفحه اصلی راهنمای سلامت</a></body></html>').encode()
    data=route_metadata(app,'/');data['indexable']=False
    files['seo/noindex.html']=metadata_html(page,data).encode()
    if snapshots is not None:
        required=['/','/about']+['/centers/'+r['id'] for r in public_records(app)]+['/categories/'+c for c in ['hospitals','pharmacies']]
        if set(snapshots)!=set(required):raise ValueError('Prerender route coverage mismatch')
        for route,body in snapshots.items():
            name='index.html' if route=='/' else route.strip('/')+'/index.html'
            if '<script' in body and re.search(r'<script(?![^>]*type="application/ld\+json")',body):raise ValueError('Unexpected script in captured content')
            files[name]=files[name].replace(b'<div id="root"></div>',('<div id="root" aria-busy="true">'+body+'</div>').encode())
    return files
