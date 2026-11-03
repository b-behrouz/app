#!/usr/bin/env python3
"""Import user-supplied local pharmacy records; keep audit inputs private.
No network, Git writes, or host publication. Images are embedded byte-for-byte.
"""
import base64,copy,hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.private/pharmacy-import'
MATCHES={'mashhad-pharmacy-markazi-emam':'pharmacy-markazi-imam','mashhad-pharmacy-22bahman-daneshgah':'pharmacy-22-bahman','mashhad-pharmacy-fakour':'pharmacy-fakour'}

def prepare(current,records,manifest,images):
    assert len(records)==20 and len({r['id'] for r in records})==20
    assert len(manifest)==36
    expected={m['path']:m for m in manifest};result=copy.deepcopy(current)
    byid={r['id']:r for r in result['records']};used=set();mapping=[]
    for r in records:
        key=MATCHES.get(r['id'],r['id']);old=byid.get(key,{})
        if old:
            assert r['phone'] in old['phones'],key
            assert old['city']==r['city']=='مشهد',key
        photos=[]
        for photo in r['photos']:
            relative=Path(photo['path']);assert relative.parent==Path('images')
            file=images/relative.name;raw=file.read_bytes();evidence=expected[photo['path']]
            assert evidence['id']==r['id'] and evidence['sha256']==hashlib.sha256(raw).hexdigest()
            assert evidence['bytes']==len(raw)
            with Image.open(file) as im:
                assert im.format=='JPEG';assert im.size==(photo['width'],photo['height']);im.verify()
            photos.append({'src':'data:image/jpeg;base64,'+base64.b64encode(raw).decode(),'alt':photo['alt'],'type':'photo','fit':'contain'})
            used.add(photo['path'])
        assert photos and r['name'] and r['address'] and r['phone'].startswith('0')
        merged=copy.deepcopy(old)
        merged.update(id=key,type='pharmacy',name=r['name'],city=r['city'],province='خراسان رضوی',address=r['address'],phones=[r['phone'],*r['additional_phones']],description=r['introduction'],services=r['services'],websites=[r['website']] if r['website'] else [],gallery=photos,image={'url':None})
        hours=r['opening_hours']
        # An explicitly unknown Friday schedule remains in private input, not UI.
        merged['hours']=hours.split('؛ جمعه نامشخص')[0] if hours else None
        aggregate=r['user_reviews']
        if aggregate and aggregate['count']>0:
            assert aggregate['scale']==5 and 0<=aggregate['rating']<=5
            merged['rating']=aggregate['rating'];merged['reviewCount']=aggregate['count']
        # Keep existing actual review texts; never synthesize them from aggregates.
        for field in ('verification','source_urls','license_verified','last_researched_at'):
            merged.pop(field,None)
        if key in byid:
            result['records'][next(i for i,x in enumerate(result['records']) if x['id']==key)]=merged
        else:result['records'].append(merged)
        mapping.append({'input_id':r['id'],'runtime_id':key,'photos':len(photos)})
    assert used==set(expected)
    # All pharmacy research metadata is archived privately, never sent to browser.
    for r in result['records']:
        if r['type']=='pharmacy':
            for key in ('verification','source_urls','license_verified','last_researched_at'):r.pop(key,None)
            if r.get('image'):r['image']={k:v for k,v in r['image'].items() if k=='url'}
    return result,mapping

def main():
    source=ROOT/'src/app.js';text=source.read_text();first,rest=text.split(';\n',1)
    current=json.loads(first.removeprefix('const HAMGHADAM_MEDICAL_DATA = '))
    baseline=PRIVATE/'previous-medical-data.json'
    if not baseline.exists():baseline.write_text(json.dumps(current,ensure_ascii=False))
    records=json.loads((PRIVATE/'pharmacies.json').read_text());manifest=json.loads((PRIVATE/'image-manifest.json').read_text())
    images=ROOT/'assets/pharmacies'
    result,mapping=prepare(current,records,manifest,images)
    (PRIVATE/'mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    source.write_text('const HAMGHADAM_MEDICAL_DATA = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n'+rest)
    print('Imported 20 targets; preserved 3 existing IDs; embedded 36 original local JPEG files.')
if __name__=='__main__':main()
