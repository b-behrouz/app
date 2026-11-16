import hashlib,json,re,sys,tempfile,unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_hosting import build
from deploy_ftps import validate_bundle
class EntityMarkup(HTMLParser):
 def __init__(self):super().__init__();self.ids=[]
 def handle_starttag(self,tag,attrs):
  data=dict(attrs)
  if 'data-entity-id' in data:self.ids.append(data['data-entity-id'])
class PrerenderTests(unittest.TestCase):
 def test_snapshots_match_source_and_each_center_has_one_own_record(self):
  data=json.loads((ROOT/'data/prerender/pages.json').read_text())
  self.assertEqual(data['source_sha256'],hashlib.sha256((ROOT/'hamghadam-preview.html').read_bytes()).hexdigest());self.assertEqual(len(data['pages']),66)
  self.assertIn('home-brand-logo',data['pages']['/']);self.assertIn('home-categories',data['pages']['/'])
  for route,body in data['pages'].items():
   self.assertNotIn('127.0.0.1',body);self.assertNotIn('data:image/',body)
   if route.startswith('/centers/'):
    parser=EntityMarkup();parser.feed(body);self.assertEqual(parser.ids,[route.rsplit('/',1)[1]])
 def test_seed_cannot_be_deployed(self):
  with tempfile.TemporaryDirectory() as directory:
   build(output=directory,skip_prerender=True)
   with self.assertRaisesRegex(ValueError,'seed cannot be deployed'):validate_bundle(Path(directory))
 def test_removed_category_is_only_a_home_redirect(self):
  files=build();legacy=files['categories/nurses/index.html'].decode()
  self.assertIn('noindex,follow',legacy);self.assertIn('0;url=/',legacy);self.assertNotIn('پرستارها',legacy)
  self.assertNotIn('nurses',files['sitemap.xml'].decode())
  pages=json.loads((ROOT/'data/prerender/pages.json').read_text())['pages'];self.assertNotIn('/categories/nurses',pages)
 def test_category_sitemap_has_only_canonical_paths(self):
  files=build();sitemap=files['sitemap.xml'].decode()
  self.assertNotIn('?category=',sitemap);self.assertIn('/categories/hospitals/',sitemap);self.assertIn('/categories/pharmacies/',sitemap)
if __name__=='__main__':unittest.main()
