import importlib.util, io, json, sys, unittest, ftplib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_hosting import build
from deploy_ftps import deploy,digest,META,safe_path
class FTP:
 def __init__(self,files=None):self.files=dict(files or {});self.fail=None;self.directories={'.'};self.deleted=[];self.calls=0
 def retrbinary(self,cmd,receive):
  name=cmd[5:]
  if name not in self.files:raise ftplib.error_perm('550 missing')
  receive(self.files[name])
 def nlst(self,parent):
  prefix='' if parent=='.' else parent+'/'
  return list({n[len(prefix):].split('/')[0] for n in self.files if n.startswith(prefix)})
 def mkd(self,name):self.directories.add(name)
 def pwd(self):return '/'
 def cwd(self,name):pass
 def storbinary(self,cmd,file):self.files[cmd[5:]]=file.read()
 def rename(self,a,b):
  self.calls+=1
  if self.fail==b:self.fail=None;raise OSError('simulated rename failure')
  self.files[b]=self.files.pop(a)
 def delete(self,name):
  if name not in self.files:raise ftplib.error_perm('550 missing')
  self.deleted.append(name);del self.files[name]
class HostingTests(unittest.TestCase):
 def setUp(self):
  self.files=build();self.meta=json.loads(self.files[META])
 def test_output_only_static_and_root_routes(self):
  self.assertEqual(len(self.files),16);self.assertLess(self.meta['bytes'],15*1024*1024)
  self.assertEqual(self.files['index.html'],(ROOT/'hamghadam-preview.html').read_bytes())
  self.assertNotIn(b'/app/#',self.files['feedback/index.html'])
  self.assertIn(b'/#/feedback',self.files['feedback/index.html'])
  self.assertEqual(len([n for n in self.files if n.startswith('centers/')]),10)
  for bad in ['.htaccess','mail/index.html','../index.html','node_modules/a','src/app.js']:self.assertFalse(safe_path(bad))
 def test_check_is_read_only(self):
  ftp=FTP({'index.html':b'other','mail/private':b'untouched'})
  before=ftp.files.copy();deploy(ftp,self.files,self.meta,check=True);self.assertEqual(ftp.files,before)
 def test_collisions_block_all_writes_and_adoption_preserves_unrelated(self):
  ftp=FTP({'index.html':b'previous','mail/private':b'email','.htaccess':b'config'})
  before=ftp.files.copy()
  with self.assertRaises(ValueError):deploy(ftp,self.files,self.meta)
  self.assertEqual(ftp.files,before)
  deploy(ftp,self.files,self.meta,digest(b'previous'))
  self.assertEqual(ftp.files['mail/private'],b'email');self.assertEqual(ftp.files['.htaccess'],b'config')
  self.assertEqual(ftp.files['index.html'],self.files['index.html'])
 def test_failure_restores_files_and_cleans_temps(self):
  ftp=FTP({'index.html':b'previous','unrelated':b'keep'});before=ftp.files.copy();ftp.fail='index.html'
  with self.assertRaises(OSError):deploy(ftp,self.files,self.meta,digest(b'previous'))
  self.assertEqual(ftp.files,before)
 def test_remote_manual_edit_refused(self):
  ftp=FTP(self.files);ftp.files['index.html']=b'manual edit'
  with self.assertRaises(ValueError):deploy(ftp,self.files,self.meta)
 def test_existing_php_refused(self):
  ftp=FTP({'index.php':b'private config'})
  with self.assertRaises(ValueError):deploy(ftp,self.files,self.meta,check=True)
if __name__=='__main__':unittest.main()
