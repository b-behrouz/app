import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from backup_hosting import backup
class ReadOnlyFTP:
 def __init__(self,values):self.values=iter(values);self.reads=[]
 def retrbinary(self,command,receive):
  if command!='RETR index.html':raise AssertionError('Unexpected remote access')
  self.reads.append(command);receive(next(self.values))
 def __getattr__(self,name):raise AssertionError('No remote mutations permitted: '+name)
class BackupTests(unittest.TestCase):
 def test_exact_bytes_and_manifest_without_remote_writes(self):
  with tempfile.TemporaryDirectory() as d:
   ftp=ReadOnlyFTP([b'<!doctype html>real old site',b'<!doctype html>real old site'])
   m=backup(ftp,d)
   self.assertEqual(Path(d,'index.html').read_bytes(),b'<!doctype html>real old site')
   self.assertEqual(len(ftp.reads),2);self.assertEqual(m['bytes'],len(b'<!doctype html>real old site'))
   self.assertEqual(json.loads(Path(d,'backup-manifest.json').read_text())['sha256'],m['sha256'])
 def test_changing_file_does_not_save_partial_backup(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):backup(ReadOnlyFTP([b'old',b'new']),d)
   self.assertEqual(list(Path(d).iterdir()),[])
if __name__=='__main__':unittest.main()
