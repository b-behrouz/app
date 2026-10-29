#!/usr/bin/env python3
"""Read-only backup of the existing public index; never backs up secrets or host configuration."""
import argparse, datetime, hashlib, json, os, ssl, sys, ftplib
from pathlib import Path
from deploy_ftps import bounded_read

def backup(ftp,output):
    output=Path(output)
    if output.exists() and any(output.iterdir()):raise ValueError('Use an empty backup destination')
    first=bounded_read(ftp,'index.html')
    if first is None:raise ValueError('No index.html to back up')
    # A second download catches a file changing during this operation.
    second=bounded_read(ftp,'index.html')
    if first!=second:raise ValueError('Remote file changed during backup; nothing saved')
    sha=hashlib.sha256(first).hexdigest()
    output.mkdir(parents=True,exist_ok=True)
    index=output/'index.html';index.write_bytes(first)
    if hashlib.sha256(index.read_bytes()).hexdigest()!=sha:raise ValueError('Local backup digest mismatch')
    manifest={'source':'FTPS read-only: public Document Root/index.html','site':'https://hamghadamcare.ir/',
              'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'bytes':len(first),'sha256':sha,'scope':'index.html only; not a full hosting, email, database or configuration backup'}
    (output/'backup-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('BACKUP VERIFIED: two FTPS reads and saved file agree; bytes='+str(len(first))+'; SHA256='+sha)
    return manifest

def backup_entries(ftp,output,revision):
    from build_hosting import build
    from deploy_ftps import digest
    names=[n for n in build(revision) if n.endswith('.html')]
    output=Path(output)
    if output.exists() and any(output.iterdir()):raise ValueError('Use an empty backup destination')
    snapshots={}
    for name in names:
        first=bounded_read(ftp,name)
        if first is None:continue
        if first!=bounded_read(ftp,name):raise ValueError('Remote target changed during backup')
        snapshots[name]=first
        if sum(map(len,snapshots.values()))>30*1024*1024:raise ValueError('Backup size budget exceeded')
    if 'index.html' not in snapshots:raise ValueError('Missing initial index')
    output.mkdir(parents=True,exist_ok=True)
    for name,data in snapshots.items():
        path=output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        if digest(path.read_bytes())!=digest(data):raise ValueError('Saved backup mismatch')
    manifest={'schema':1,'site':'https://hamghadamcare.ir/','target_revision':revision,
      'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'files':{name:digest(data) for name,data in snapshots.items()},
      'scope':'Only existing public HTML entrypoints of the approved release; not full hosting backup'}
    raw=(json.dumps(manifest,sort_keys=True)+'\n').encode()
    (output/'adoption-manifest.json').write_bytes(raw)
    print('PUBLIC ENTRYPOINT BACKUP VERIFIED:',len(snapshots),'files; no remote writes.')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as out:out.write('manifest_sha256='+digest(raw)+'\n')
    return manifest

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--entrypoints-revision');a=p.parse_args()
    root=os.environ['HOSTING_REMOTE_DIR']
    if not root.startswith('/') or any(x in root for x in ['\r','\n','..']):raise ValueError('Invalid destination root')
    context=ssl.create_default_context();context.minimum_version=ssl.TLSVersion.TLSv1_2
    ftp=ftplib.FTP_TLS(context=context,timeout=45)
    try:
        ftp.connect(os.environ['HOSTING_FTPS_HOST'],int(os.environ['HOSTING_FTPS_PORT']))
        ftp.auth();ftp.login(os.environ['HOSTING_FTPS_USER'],os.environ['HOSTING_FTPS_PASSWORD'])
        ftp.prot_p();ftp.set_pasv(True);ftp.cwd(root)
        if a.entrypoints_revision:backup_entries(ftp,a.output,a.entrypoints_revision)
        else:backup(ftp,a.output)
    finally:ftp.close()
if __name__=='__main__':
    try:main()
    except Exception as error:
        print('Read-only backup failed ('+type(error).__name__+'); no host files were written.',file=sys.stderr)
        sys.exit(1)
