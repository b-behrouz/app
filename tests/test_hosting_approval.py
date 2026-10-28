import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from hosting_approval import authorize
class ApprovalTests(unittest.TestCase):
 def args(self,**changes):
  sha='a'*40
  a=dict(event='workflow_dispatch',ref='refs/heads/main',operation='deploy',revision=sha,approved_revision=sha,confirmation='DEPLOY hamghadamcare.ir '+sha,enabled='true',current='b'*40,is_ancestor=lambda _:True);a.update(changes);return a
 def test_exact_manual_approval(self):self.assertEqual(authorize(**self.args()),'a'*40)
 def test_push_ci_and_prior_approval_cannot_publish(self):
  for change in [dict(event='push'),dict(event='workflow_run'),dict(ref='refs/heads/other'),dict(approved_revision='b'*40),dict(confirmation='DEPLOY'),dict(enabled='false'),dict(revision='main'),dict(is_ancestor=lambda _:False)]:
   with self.subTest(change=change),self.assertRaises(ValueError):authorize(**self.args(**change))
 def test_check_cannot_select_deploy_and_needs_no_enable(self):
  self.assertEqual(authorize(**self.args(operation='check',enabled='false',revision='',approved_revision='',confirmation='')),'b'*40)
 def test_rollback_is_an_independent_operation(self):
  with self.assertRaises(ValueError):authorize(**self.args(operation='rollback'))
  self.assertEqual(authorize(**self.args(operation='rollback',confirmation='ROLLBACK hamghadamcare.ir '+'a'*40)),'a'*40)
 def test_no_automatic_trigger_in_prepared_workflow(self):
  s=Path('.github/workflows/deploy-hosting.yml').read_text()
  self.assertNotIn('  push:',s);self.assertNotIn('  workflow_run:',s);self.assertIn('  workflow_dispatch:',s)
if __name__=='__main__':unittest.main()
