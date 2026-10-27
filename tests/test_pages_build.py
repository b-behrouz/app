import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_pages import files
class PagesBuildTests(unittest.TestCase):
 def test_site_is_the_index_and_readme_is_preserved(self):
  self.assertEqual((ROOT/'index.html').read_bytes(),(ROOT/'hamghadam-preview.html').read_bytes())
  self.assertIn('<div id="root"></div>',(ROOT/'index.html').read_text())
  self.assertTrue((ROOT/'README.md').is_file());self.assertTrue((ROOT/'.nojekyll').is_file())
 def test_all_known_routes_have_physical_entry_files(self):
  manifest=json.loads((ROOT/'.pages-manifest.json').read_text())
  self.assertEqual(manifest['base_path'],'/app/');self.assertEqual(len(manifest['routes']),20)
  for route in manifest['routes']:
   data=(ROOT/route.lstrip('/')/'index.html').read_text()
   self.assertIn('/app/#'+route,data)
 def test_build_is_current(self):
  for name,data in files().items():self.assertEqual((ROOT/name).read_bytes(),data,name)
if __name__=='__main__':unittest.main()
