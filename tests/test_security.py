"""Verify credential gates reject representative secrets without printing their values."""
import contextlib,io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_project import scan,sensitive_path
class SecurityTests(unittest.TestCase):
 def test_sensitive_paths(self):
  for name in ['.env','.env.production','key.pem','credentials.json','config/preview.local.json']:
   self.assertTrue(sensitive_path(name),name)
  self.assertFalse(sensitive_path('config/preview.example.json'))
 def test_secret_redaction(self):
  sample=b'ghp_'+b'Z'*36
  out=io.StringIO();err=io.StringIO()
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
   with self.assertRaises(SystemExit):scan([('sample.js',sample)])
  self.assertNotIn(sample.decode(),out.getvalue()+err.getvalue())
  self.assertIn('GitHub credential',err.getvalue())
 def test_public_endpoint_is_not_a_password(self):
  with contextlib.redirect_stdout(io.StringIO()):
   scan([('config/preview.example.json',b'{"apps_script_url":""}')])
if __name__=='__main__':unittest.main()
