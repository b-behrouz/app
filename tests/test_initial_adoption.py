import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from backup_hosting import backup_entries
from deploy_ftps import validate_adoption,deploy,META
from build_hosting import build
from test_hosting import FTP
SHA='081ca34056de8a659696c53f382409582c6b36e3'
class AdoptionTests(unittest.TestCase):
 def snapshot(self,ftp,d):
  backup_entries(ftp,d,SHA)
  h=hashlib.sha256((Path(d)/'adoption-manifest.json').read_bytes()).hexdigest()
  return validate_adoption(d,h,SHA),h
 def test_only_exact_backed_up_public_targets_can_be_adopted(self):
  old={'index.html':b'old home','centers/hamghadam-local-05/index.html':b'old center','unrelated.txt':b'keep','.htaccess':b'keep config'}
  ftp=FTP(old);files=build(SHA);meta=json.loads(files[META])
  with tempfile.TemporaryDirectory() as d:
   adoption,h=self.snapshot(ftp,d)
   self.assertEqual(ftp.files,old)
   self.assertEqual(set(adoption),{'index.html','centers/hamghadam-local-05/index.html'})
   deploy(ftp,files,meta,adoption=adoption)
   self.assertEqual(ftp.files['index.html'],files['index.html'])
   self.assertEqual((Path(d)/'centers/hamghadam-local-05/index.html').read_bytes(),b'old center')
   self.assertEqual(ftp.files['unrelated.txt'],b'keep');self.assertEqual(ftp.files['.htaccess'],b'keep config')
 def test_file_changed_after_backup_is_refused_before_writing(self):
  ftp=FTP({'index.html':b'old'});files=build(SHA)
  with tempfile.TemporaryDirectory() as d:
   adoption,_=self.snapshot(ftp,d);ftp.files['index.html']=b'newer manual edit';before=ftp.files.copy()
   with self.assertRaises(ValueError):deploy(ftp,files,json.loads(files[META]),adoption=adoption)
   self.assertEqual(ftp.files,before)
 def test_digest_revision_or_tampered_bytes_are_refused(self):
  with tempfile.TemporaryDirectory() as d:
   ftp=FTP({'index.html':b'old'});_,h=self.snapshot(ftp,d)
   with self.assertRaises(ValueError):validate_adoption(d,'0'*64,SHA)
   with self.assertRaises(ValueError):validate_adoption(d,h,'f'*40)
   (Path(d)/'index.html').write_bytes(b'altered')
   with self.assertRaises(ValueError):validate_adoption(d,h,SHA)
if __name__=='__main__':unittest.main()
