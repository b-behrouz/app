"""Protect lossless assets, crawlable routes and sitemap scope during migration."""
import hashlib,re,sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_hosting import build
from build_pages import public_records,route_metadata
from site_assets import externalize
class DomainAssetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.files=build();cls.app=(ROOT/'src/app.js').read_text();cls.records=public_records(cls.app)
 def test_every_extracted_image_is_lossless_and_present(self):
  transformed,assets=externalize((ROOT/'hamghadam-preview.html').read_text())
  self.assertEqual(len(assets),50);self.assertNotIn('data:image/',transformed)
  for name,data in assets.items():self.assertEqual(self.files[name],data);self.assertEqual((ROOT/name).read_bytes(),data)
 def test_each_entity_has_its_own_initial_canonical_and_title(self):
  self.assertEqual(len(self.records),62)
  for record in self.records:
   route='/centers/'+record['id'];html=self.files[route.lstrip('/')+'/index.html'].decode();meta=route_metadata(self.app,route)
   self.assertIn(meta['title'],html);self.assertIn('rel="canonical" href="https://rahnamasalamat.ir'+route+'/"',html);self.assertNotIn('hamghadamcare.ir',html)
 def test_sitemap_excludes_forms_aliases_and_unknown_pages(self):
  root=ET.fromstring(self.files['sitemap.xml']);urls=[e.text for e in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
  self.assertEqual(len(urls),66);self.assertEqual(len(set(urls)),66)
  for url in urls:self.assertTrue(url.startswith('https://rahnamasalamat.ir/'));self.assertNotRegex(url,r'(?:feedback|introduce-center|family-need|/need/|404)')
  for route in ['need','feedback','introduce-center','family-need']:self.assertIn('noindex,follow',self.files[route+'/index.html'].decode())
 def test_matomo_and_api_identity_preserved(self):
  self.assertIn('https://hamghadamcareir.matomo.cloud/matomo.php',self.app);self.assertIn('siteId:`1`',self.app)
  self.assertIn('[`rahnamasalamat.ir`,`www.rahnamasalamat.ir`,this.win.location.hostname]',self.app)
  self.assertNotIn('https://hamghadamcare.ir/',self.app)
if __name__=='__main__':unittest.main()
