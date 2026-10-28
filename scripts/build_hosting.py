#!/usr/bin/env python3
"""Build only static production files; keep GitHub Pages and local preview unchanged."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
from build_preview import ROOT
from build_pages import expected_files

def build(revision=None, output=None):
    def read(name):
        return subprocess.check_output(['git','show',revision+':'+name],cwd=ROOT) if revision else (ROOT/name).read_bytes()
    preview=read('hamghadam-preview.html')
    app=read('src/app.js').decode()
    generated=expected_files(preview,app,{'base_path':'/'})
    files={name:data for name,data in generated.items() if name.endswith('.html')}
    assert 'index.html' in files and all(not name.startswith('.') for name in files)
    total=sum(map(len,files.values()))
    if total > 15*1024*1024:raise ValueError('Production bundle exceeds 15 MiB budget')
    manifest={'schema':1,'revision':revision or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'files':{name:hashlib.sha256(data).hexdigest() for name,data in files.items()},'bytes':total}
    files['.hamghadam-deploy.json']=(json.dumps(manifest,sort_keys=True)+'\n').encode()
    if output:
        output=Path(output)
        if output.exists() and any(output.iterdir()):raise ValueError('Use a fresh output directory')
        for name,data in files.items():
            p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return files
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--revision');parser.add_argument('--output',required=True);args=parser.parse_args()
    result=build(args.revision,args.output);print('Production:',len(result),'files,',sum(map(len,result.values())),'bytes; base path /')
