"""Deterministic, lossless extraction for production; standalone preview stays inline."""
import base64,hashlib,re
IMAGE=re.compile(r'data:image/(jpeg|png|webp|gif);base64,[A-Za-z0-9+/=]+')
def externalize(html):
    assets={}
    def replace(match):
        uri=match.group();data=base64.b64decode(uri.split(',',1)[1],validate=True)
        ext={'jpeg':'jpg'}.get(match.group(1),match.group(1))
        name='assets/site/image-'+hashlib.sha256(data).hexdigest()[:24]+'.'+ext
        if name in assets and assets[name]!=data:raise ValueError('Asset hash collision')
        assets[name]=data
        return '/'+name
    return IMAGE.sub(replace,html),assets

if __name__=='__main__':
    from build_preview import ROOT,render
    _,assets=externalize(render().decode())
    for name,data in assets.items():
        path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('Extracted',len(assets),'unique image files without recompression.')
