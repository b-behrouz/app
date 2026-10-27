#!/usr/bin/env python3
"""Reassemble the supplied runtime without rewriting HTML, script or style bytes."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
def render(config=None):
    template=(ROOT/'src/index.template.html').read_text(encoding='utf-8')
    def inline(match):
        name=match.group(1)
        if name not in {'app.js','style-1.css','style-2.css','style-3.css'}:
            raise ValueError('Unexpected inline source: '+name)
        return (ROOT/'src'/name).read_text(encoding='utf-8')
    html=re.sub(r'<!-- INLINE:([a-z0-9.-]+) -->',inline,template)
    if config:
        values=json.loads(Path(config).read_text(encoding='utf-8'))
        endpoint=values.get('apps_script_url','')
        if endpoint and not re.fullmatch(r'https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec',endpoint):
            raise ValueError('Invalid Apps Script deployment URL')
        html=re.sub(r"const HAMGHADAM_CENTER_ENDPOINT = '[^']*';",lambda _:f"const HAMGHADAM_CENTER_ENDPOINT = '{endpoint}';",html,count=1)
    return html.encode('utf-8')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--config',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'hamghadam-preview.html')
    args=parser.parse_args();expected=render(args.config)
    if args.check:
        if not args.output.exists() or args.output.read_bytes()!=expected:
            raise SystemExit('HTML is stale. Run python3 scripts/build_preview.py')
        print('PASS: HTML exactly matches the source assembly.')
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(expected)
        print('Built:',args.output)
