const {chromium}=require('playwright'),fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync('src/app.js','utf8'),html=fs.readFileSync('hamghadam-preview.html','utf8');
const care=vm.runInNewContext(source.match(/var ld=JSON.parse\(`(.*?)`\)/s)[0].replace(/^var ld=/,''));
const medical=JSON.parse(source.match(/const HAMGHADAM_MEDICAL_DATA = (\{.*?\});/s)[1]).records;
const samples=[...care.slice(0,3),...medical.filter(r=>r.type==='hospital').slice(0,3),...medical.filter(r=>r.type==='pharmacy').slice(0,3)];
(async()=>{const b=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});try{
 for(const width of [320,390,1440]){
  const c=await b.newContext({viewport:{width,height:900}}),errors=[],requests=[];await c.route('**/*',r=>{requests.push(r.request().url());return r.request().url().startsWith('https://entities.test/')?r.fulfill({contentType:'text/html',body:html}):r.abort();});const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));
  for(const record of samples){
   await p.goto('https://entities.test/#/centers/'+record.id);await p.locator('[data-entity-id="'+record.id+'"]').waitFor();
   const kind=record.type||'care';assert.equal(await p.locator('.entity-detail').getAttribute('data-entity-kind'),kind);assert.equal(await p.locator('h1').innerText(),record.fullName||record.name);
   const phones=kind==='care'?record.phones.filter(x=>x.publicationAllowed&&x.formatValid).map(x=>x.number):record.phones;
   const links=await p.locator('a[href^="tel:"]').evaluateAll(es=>[...new Set(es.map(e=>e.getAttribute('href').slice(4)))]);assert.deepEqual(links.sort(),[...new Set(phones)].sort());
   const addresses=[...(record.details?.addresses||[]),...(record.address?[record.address]:[])];for(const address of addresses)assert((await p.locator('.entity-detail').innerText()).includes(address));
   const map=p.locator('.entity-map');assert.equal(await map.count(),0);assert.equal(await p.locator('.entity-type,.entity-sources').count(),0);assert.equal(await p.locator('.entity-heading > :not(h1)').count(),0);assert.equal(await p.locator('a').filter({hasText:/^منبع(?: |$)/}).count(),0);
   assert.equal(await p.locator('.hamghadam-bottom-nav').count(),0);assert.equal(await p.locator('.profile-back').count(),1);
   const action=await p.locator('.entity-actions [data-slot=button]').evaluateAll(es=>es.map(e=>({h:e.getBoundingClientRect().height,r:getComputedStyle(e).borderRadius})));assert(action.every(a=>a.h===48));assert(action.every(a=>a.r===action[0].r));assert.equal(action.length,1);const callWidth=await p.locator('.entity-call').evaluate(e=>e.getBoundingClientRect().width),containerWidth=await p.locator('.entity-actions').evaluate(e=>e.getBoundingClientRect().width);assert.equal(callWidth,containerWidth);
   if(kind!=='care'){assert.equal(await p.locator('[data-rating-value]').count(),0);assert.equal(await p.getByRole('tab',{name:'نظرات',exact:true}).count(),0);assert.equal(await p.getByText('ساعت کاری',{exact:true}).count(),0);const schema=JSON.parse(await p.locator('[data-medical-profile-schema]').textContent());assert.equal(schema.name,record.name);assert.equal(schema.telephone,record.phones[0]);assert.equal(schema.address.streetAddress,record.address);}
   if(!(record.gallery?.length||record.image?.url))assert.equal(await p.locator('[data-profile-gallery]').count(),0);
   const about=p.getByRole('tab',{name:'معرفی و خدمات',exact:true});if(await about.count()){
    await about.click();const details=await p.locator('.entity-detail').innerText();const services=[...new Set([...(record.details?.services||[]),...(record.services||[]),...(record.careServices||[]),...(record.nursingServices||[])])];for(const service of services)assert(details.includes(service));for(const text of [record.description,record.bio].filter(Boolean))assert(details.includes(text));for(const url of record.source_urls||[])assert.equal(await p.locator('a').evaluateAll((es,u)=>es.filter(e=>e.getAttribute('href')===u).length,url),0);
   }
   await p.evaluate(()=>window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'}));const lastCard=p.locator('.entity-detail [data-slot=card]:visible').last();if(await lastCard.count()){assert((await lastCard.boundingBox()).y+(await lastCard.boundingBox()).height<=(await p.locator('.entity-actions').boundingBox()).y+1,'Last content must scroll above the contact footer');}assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   if([samples[0].id,samples[3].id,samples[6].id].includes(record.id)){const generalTab=p.getByRole('tab',{name:'عمومی',exact:true});if(await generalTab.count())await generalTab.click();fs.mkdirSync('work/qa/entities',{recursive:true});await p.screenshot({path:`work/qa/entities/${width}-${record.id}.png`,fullPage:true});}
   console.log('PASS record',width,record.id);
  }
  // Route identity resets the selected tab, and unknown IDs cannot borrow another record.
  await p.goto('https://entities.test/#/centers/does-not-exist');await p.getByText('مرکز پیدا نشد',{exact:true}).waitFor();assert.equal(await p.locator('.entity-detail').count(),0);assert.equal(await p.locator('a[href^="tel:"]').count(),0);
  // Direct entry returns to the matching category; list entry retains search and category.
  const direct=await c.newPage();await direct.goto('https://entities.test/#/centers/'+samples[3].id);await direct.locator('.profile-back').click();await direct.locator('[data-home-ready=true]').waitFor();assert(direct.url().includes('category=hospitals'));await direct.getByRole('searchbox').fill('قائم');await direct.locator('.directory-record-details').first().click();await direct.locator('.profile-back').click();await direct.locator('[data-home-ready=true]').waitFor();assert.equal(await direct.getByRole('searchbox').inputValue(),'قائم');assert(direct.url().includes('category=hospitals'));await direct.close();
  assert.deepEqual(errors,[]);await c.close();console.log('PASS shared detail layout, real record isolation, full-width 48px contact, optional sections, hidden sources/type/map, back navigation and RTL:',width);
 }
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
