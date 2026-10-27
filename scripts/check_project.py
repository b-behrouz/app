#!/usr/bin/env python3
"""Deterministic assembly, offline asset checks, syntax and credential screening."""
from pathlib import Path
from html.parser import HTMLParser
import argparse,re,subprocess,sys
from build_preview import ROOT,render
from build_pages import expected_files,files
import json
PATTERNS={
 'private key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'GitHub credential':re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})'),
 'Google API key':re.compile(rb'AIza[0-9A-Za-z_-]{35}'),
 'AWS access key':re.compile(rb'(?:AKIA|ASIA)[A-Z0-9]{16}'),
 'Slack credential':re.compile(rb'xox[baprs]-[0-9A-Za-z-]{20,}'),
 'credential URL':re.compile(rb'https?://[^\s/<>"\x27]{1,80}:[^\s/@<>"\x27]{3,160}@'),
 'assigned secret':re.compile(rb'''(?i)(?:api_secret|client_secret|private_key|access_token|refresh_token|password)\s*[=:]\s*["'][A-Za-z0-9_+/=-]{16,}["']''')
}
def git(*args):
 return subprocess.check_output(['git',*args],cwd=ROOT)
def sensitive_path(name):
 p=Path(name);lower=p.name.lower()
 return (lower=='.env' or lower.startswith('.env.') and lower!='.env.example'
   or p.suffix.lower() in {'.pem','.key'}
   or any(part in {'.git','node_modules','.private'} for part in p.parts)
   or lower.startswith(('credentials','client_secret')) and lower.endswith('.json')
   or 'service-account' in lower and lower.endswith('.json')
   or name=='config/preview.local.json')
def candidates():
 for line in git('ls-files','--cached','--others','--exclude-standard','-z').split(b'\0'):
  if line:
   name=line.decode();p=ROOT/name
   if p.is_file():yield name,p.read_bytes()
def scan(items):
 errors=[];count=0
 for name,data in items:
  count+=1
  if sensitive_path(name):errors.append((name,'sensitive path'));continue
  for label,pattern in PATTERNS.items():
   if pattern.search(data):errors.append((name,label))
 if errors:
  for name,label in errors:print('BLOCKED:',name,'('+label+')',file=sys.stderr)
  raise SystemExit('Credential screening failed. Values were not printed.')
 print(f'PASS: screened {count} files; no matched credential patterns. This is not a proof of absence of secrets.')
class AssetCheck(HTMLParser):
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  targets=[]
  if tag in {'script','img','source','iframe','video','audio'} and d.get('src'):targets.append(d['src'])
  if tag=='link' and d.get('rel') in {'stylesheet','preload','modulepreload','icon'} and d.get('href'):targets.append(d['href'])
  for target in targets:
   if not target.startswith(('data:','#')):raise ValueError('External essential asset in HTML: '+tag)
  if d.get('srcset'):raise ValueError('Review srcset for self-contained delivery')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--staged',action='store_true');args=parser.parse_args()
 if args.staged:
  names=git('diff','--cached','--name-only','--diff-filter=ACM','-z').split(b'\0')
  scan((n.decode(),git('show',':'+n.decode())) for n in names if n)
  # Build the staged source, not an unrelated version in the worktree.
  source_names=['src/index.template.html','src/app.js','src/style-1.css','src/style-2.css','src/style-3.css','hamghadam-preview.html']
  sources={n:git('show',':'+n).decode('utf-8') for n in source_names}
  assembled=re.sub(r'<!-- INLINE:([a-z0-9.-]+) -->',lambda m:sources['src/'+m[1]],sources['src/index.template.html'])
  if assembled!=sources['hamghadam-preview.html']:raise SystemExit('Staged HTML does not match staged sources')
  pages=expected_files(assembled.encode(),sources['src/app.js'],json.loads(git('show',':config/pages.json')))
  for name,data in pages.items():
   if git('show',':'+name)!=data:raise SystemExit('Staged Pages output mismatch: '+name)
  print('PASS: staged preview and Pages outputs match staged sources.');return
 scan(candidates())
 html=render()
 if (ROOT/'hamghadam-preview.html').read_bytes()!=html:raise SystemExit('HTML must be rebuilt')
 for name,data in files().items():
  if not (ROOT/name).exists() or (ROOT/name).read_bytes()!=data:raise SystemExit('Pages output must be rebuilt: '+name)
 text=html.decode('utf-8');AssetCheck().feed(text)
 for p in sorted((ROOT/'src').glob('*.css')):
  css=p.read_text()
  if re.search(r'@import\s',css):raise SystemExit('External CSS import requires review')
  for target in re.findall(r'url\(\s*[\x27\"]?([^\s\x27\")]+)',css):
   if not target.startswith(('data:','#')):raise SystemExit('CSS asset is not embedded')
 if not re.search(r'<html[^>]*lang="fa-IR"[^>]*dir="rtl"',text):raise SystemExit('Document language/direction changed')
 if '<meta name="description"' not in text or '<title>' not in text:raise SystemExit('SEO tags missing')
 if '<div id="root"></div>' not in text:raise SystemExit('Review original render root before changing it')
 subprocess.run(['node','--input-type=module','--check'],input=(ROOT/'src/app.js').read_bytes(),check=True)
 print('PASS: reproducible HTML, embedded essential assets, JavaScript syntax and existing SEO shell.')
if __name__=='__main__':main()
