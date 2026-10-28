#!/usr/bin/env python3
"""Explicit FTPS only. No mirror/delete. Secrets come exclusively from the environment."""
import argparse, datetime, ftplib, hashlib, io, json, os, re, ssl, sys, urllib.request, uuid
from pathlib import Path, PurePosixPath
META='.hamghadam-deploy.json'
LIMIT=16*1024*1024

def digest(data):return hashlib.sha256(data).hexdigest()
def safe_path(name):
    return name in {'index.html','404.html',META} or bool(re.fullmatch(r'(?:need|feedback|introduce-center|centers/[a-z0-9-]+)/index\.html',name))
def bounded_read(ftp,name,limit=LIMIT):
    chunks=[];size=0
    def receive(data):
        nonlocal size
        size+=len(data)
        if size>limit:raise ValueError('Remote file exceeds read limit')
        chunks.append(data)
    try:ftp.retrbinary('RETR '+name,receive)
    except ftplib.error_perm as error:
        # Only treat absence as missing after listing the parent, not arbitrary 550 errors.
        if not str(error).startswith('550'):raise
        parent='.'
        for part in PurePosixPath(name).parts:
            listing=ftp.nlst(parent)
            if not any(PurePosixPath(p.rstrip('/')).name==part for p in listing):return None
            parent=part if parent=='.' else parent+'/'+part
        raise
    return b''.join(chunks)

def validate_bundle(directory):
    files={p.relative_to(directory).as_posix():p.read_bytes() for p in directory.rglob('*') if p.is_file()}
    if not files or not all(safe_path(n) for n in files):raise ValueError('Unexpected production file')
    meta=json.loads(files[META]);expected=meta['files']
    if set(files)!=(set(expected)|{META}) or any(digest(files[n])!=h for n,h in expected.items()):raise ValueError('Bundle digest mismatch')
    if sum(map(len,files.values()))>15*1024*1024:raise ValueError('Bundle budget exceeded')
    return files,meta

def deploy(ftp,files,meta,initial_hash='',check=False):
    if any(PurePosixPath(name.rstrip('/')).name=='index.php' for name in ftp.nlst('.')):
        raise ValueError('Existing index.php requires manual DocumentRoot review')
    oldraw=bounded_read(ftp,META,65536);old=json.loads(oldraw) if oldraw else None
    if old and (old.get('schema')!=1 or not all(safe_path(n) and n!=META for n in old.get('files',{}))):raise ValueError('Unknown remote manifest; refusing adoption')
    print('Checking ownership of production targets (read only).')
    current={n:bounded_read(ftp,n) for n in files}
    if check:
        print('FTPS control, encrypted passive data and remote read succeeded.')
        print('Existing index SHA256:',digest(current['index.html']) if current['index.html'] is not None else 'absent')
        print('Managed deployment:',bool(old));return
    for name,data in current.items():
        if data is None or data==files[name]:continue
        if name==META and old:continue
        if old and old['files'].get(name)==digest(data):continue
        if not old and name=='index.html' and initial_hash and digest(data)==initial_hash:continue
        raise ValueError('Remote file collision or out-of-band edit: '+name)
    # Snapshot only managed targets in memory, never read email/config/source directories.
    # All new bytes are staged and read back BEFORE replacing any live file.
    token=uuid.uuid4().hex;staged={};changed=[]
    try:
        print('Staging encrypted uploads and verifying readback.')
        for name,data in files.items():
            if current[name]==data:continue
            parent=PurePosixPath(name).parent
            parts=parent.parts
            for i in range(len(parts)):
                path='/'.join(parts[:i+1])
                try:ftp.mkd(path)
                except ftplib.error_perm:
                    here=ftp.pwd();ftp.cwd(path);ftp.cwd(here)
            temporary=str(parent/('.hamghadam-upload-'+token+'-'+digest(name.encode())[:12]))
            staged[name]=temporary
            ftp.storbinary('STOR '+temporary,io.BytesIO(data))
            if bounded_read(ftp,temporary)!=data:raise ValueError('Staged readback mismatch')
        order=sorted(n for n in staged if n not in {'index.html',META})+[n for n in ['index.html',META] if n in staged]
        print('Replacing verified managed files.')
        for name in order:
            ftp.rename(staged[name],name);changed.append(name)
        print('Upload committed; checking public URL is still required.')
    except Exception:
        # Restore only files changed by this invocation. Never recursive delete.
        failed=False
        for name in reversed(changed):
            try:
                if current[name] is None:ftp.delete(name)
                else:
                    temp=str(PurePosixPath(name).parent/('.hamghadam-restore-'+token))
                    ftp.storbinary('STOR '+temp,io.BytesIO(current[name]));ftp.rename(temp,name)
            except Exception:failed=True
        if failed:print('ROLLBACK INCOMPLETE: restore the last successful revision.',file=sys.stderr)
        raise
    finally:
        for name in staged.values():
            try:ftp.delete(name)
            except ftplib.error_perm:pass

def public_check(expected):
    url=os.environ['HOSTING_PUBLIC_URL'].rstrip('/')+'/'
    if url!='https://hamghadamcare.ir/':raise ValueError('Unexpected public URL or HTTPS is not configured')
    req=urllib.request.Request(url+'?hamghadam_verify='+uuid.uuid4().hex,headers={'Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=45) as response:
        if response.url.split('?')[0]!=url:raise ValueError('Unexpected public redirect')
        data=response.read(LIMIT+1)
    if digest(data)!=digest(expected):raise ValueError('Public HTML differs from uploaded release; inspect DNS/cache/document root')
    print('LIVE HTML VERIFIED: HTTPS certificate and SHA256 match uploaded index.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    files,meta=validate_bundle(a.directory)
    root=os.environ['HOSTING_REMOTE_DIR']
    if not root.startswith('/') or any(x in root for x in ['\r','\n','..']):raise ValueError('Use an absolute chroot-relative destination')
    context=ssl.create_default_context();context.minimum_version=ssl.TLSVersion.TLSv1_2
    ftp=ftplib.FTP_TLS(context=context,timeout=45)
    try:
        print('Connecting to FTPS control channel; requiring valid TLS 1.2+.')
        ftp.connect(os.environ['HOSTING_FTPS_HOST'],int(os.environ['HOSTING_FTPS_PORT']))
        ftp.auth() # AUTH TLS must succeed before credentials are sent; never downgrade.
        print('TLS authenticated; logging in with protected credentials.')
        ftp.login(os.environ['HOSTING_FTPS_USER'],os.environ['HOSTING_FTPS_PASSWORD'])
        print('Requiring encrypted passive data channel.')
        ftp.prot_p();ftp.set_pasv(True);ftp.cwd(root)
        deploy(ftp,files,meta,os.environ.get('HOSTING_INITIAL_INDEX_SHA256',''),a.check)
        if not a.check:public_check(files['index.html'])
    finally:ftp.close()
if __name__=='__main__':
    try:main()
    except Exception as error:
        # Server error messages can echo account/path data. Do not log exception strings.
        print('FTPS deployment/check failed ('+type(error).__name__+'). No plaintext fallback. Review connection, TLS, quota, collision and public verification.',file=sys.stderr)
        sys.exit(1)
