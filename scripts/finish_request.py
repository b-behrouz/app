#!/usr/bin/env python3
"""After explicit user approval, check, commit selected request files and verify a normal push."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args,capture=False):
 result=subprocess.run(args,cwd=ROOT,check=True,text=True,stdout=subprocess.PIPE if capture else None)
 return result.stdout.strip() if capture else None
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--message',required=True)
 parser.add_argument('--approved-push',action='store_true',help='Use only after the user reviews the delivered HTML and explicitly approves this push')
 parser.add_argument('--paths',nargs='+',required=True,help='Explicit files/directories belonging to this request; never use dot')
 parser.add_argument('--browser',action='store_true',help='Run simulated browser integration tests as well')
 args=parser.parse_args()
 if not args.approved_push:
  raise SystemExit('Push is disabled until the delivered HTML has been reviewed and explicitly approved. Do not add --approved-push without that approval.')
 branch=run('git','symbolic-ref','--short','HEAD',capture=True)
 remote=run('git','remote','get-url','origin',capture=True)
 if remote not in {'https://github.com/b-behrouz/app.git','git@github.com:b-behrouz/app.git'}:
  raise SystemExit('Unexpected origin; review the destination before continuing')
 if run('git','diff','--cached','--name-only',capture=True):raise SystemExit('Index already contains staged work; preserve it and review manually')
 names=[]
 for value in args.paths:
  p=Path(value)
  if p.is_absolute() or '..' in p.parts or value in {'.','./'} or not p.parts or p.parts[0]=='.git':
   raise SystemExit('Use explicit repository-relative request paths')
  names.append(p.as_posix())
 def selected(path):return any(path==n or path.startswith(n.rstrip('/')+'/') for n in names)
 # Source assembly includes every source file: never bundle unrelated dirty source changes.
 dirty_sources=set(run('git','diff','--name-only','--','src',capture=True).splitlines())
 dirty_sources.update(run('git','ls-files','--others','--exclude-standard','--','src',capture=True).splitlines())
 for path in dirty_sources:
  if not selected(path):raise SystemExit('Unselected source modification: '+path)
 run(sys.executable,'scripts/build_preview.py')
 run(sys.executable,'scripts/build_pages.py')
 run(sys.executable,'scripts/check_project.py')
 run('node','tests/test_center_server.cjs')
 run('node','tests/test_center_origin.cjs')
 run(sys.executable,'-m','unittest','discover','-s','tests','-p','test_security.py')
 run(sys.executable,'-m','unittest','discover','-s','tests','-p','test_pages_build.py')
 if args.browser:
  run('node','tests/test_center_browser.cjs')
  run('node','tests/test_form_alerts.cjs')
  run('node','tests/test_pages.cjs')
 run('git','diff','--check')
 # Include only generated outputs from this exact source assembly, plus removals in the old manifest.
 import json
 generated_paths=set(json.loads((ROOT/'.pages-manifest.json').read_text())['files'])
 generated_paths.update(['hamghadam-preview.html','.pages-manifest.json'])
 previous=subprocess.run(['git','show','HEAD:.pages-manifest.json'],cwd=ROOT,text=True,capture_output=True)
 if previous.returncode==0:generated_paths.update(json.loads(previous.stdout)['files'])
 for generated in sorted(generated_paths):
  if run('git','status','--porcelain','--',generated,capture=True) and generated not in names:names.append(generated)
 run('git','add','--',*names)
 run(sys.executable,'scripts/check_project.py','--staged')
 run('git','diff','--cached','--check')
 if run('git','diff','--cached','--name-only',capture=True):run('git','commit','-m',args.message)
 else:print('No new changes to commit; checking for unpushed commits.')
 sha=run('git','rev-parse','HEAD',capture=True)
 try:
  run('git','push','-u','origin',branch)
  actual=run('git','ls-remote','origin','refs/heads/'+branch,capture=True).split()
  if not actual or actual[0]!=sha:raise RuntimeError('Remote tip differs from the committed version')
 except (subprocess.CalledProcessError,RuntimeError) as error:
  raise SystemExit('COMMITTED BUT PUSH NOT VERIFIED. Local commit: '+sha+'; '+str(error))
 print('PUSH VERIFIED:',branch,sha)
if __name__=='__main__':main()
