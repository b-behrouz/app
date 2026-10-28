// Offline production-bundle QA. Never sends form data or contacts the real host.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(process.env.HAMGHADAM_HOSTING_DIR||'work/hosting');
(async()=>{const b=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});try{
 for(const width of [390,1440]){
  const c=await b.newContext({viewport:{width,height:900}});await c.route('**/*',r=>{
   const u=new URL(r.request().url());if(u.origin!=='https://hosting.test')return r.abort();
   let relative=decodeURIComponent(u.pathname).replace(/^\//,'');if(!relative||relative.endsWith('/'))relative+='index.html';
   const f=path.resolve(root,relative);if(!f.startsWith(root+path.sep))return r.abort();
   return r.fulfill({status:fs.existsSync(f)?200:404,contentType:'text/html',body:fs.readFileSync(fs.existsSync(f)?f:path.join(root,'404.html'))});
  });const p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto('https://hosting.test/');await p.locator('.hero-heading').waitFor();assert(Number(await p.locator('#center-search-results').getAttribute('data-result-count'))>0);
  await p.locator('input[type=search]').fill('zzzznotfound');await p.locator('#center-search-results[data-result-count="0"]').waitFor();
  for(const route of ['feedback','introduce-center','centers/ibn-sina-mashhad']){
   await p.goto('https://hosting.test/'+route+'/');await p.waitForURL('https://hosting.test/#/'+route);await p.reload();
   if(route==='feedback')await p.locator('.feedback-form').waitFor();
   if(route==='introduce-center')await p.locator('.center-referral-form').waitFor();
   if(route.startsWith('centers/'))await p.locator('.profile-route').waitFor();
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  }
  assert.deepEqual(errors,[]);await c.close();console.log('PASS offline production root bundle:',width);
 }
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
