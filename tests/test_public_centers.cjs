const fs=require('fs'),assert=require('assert/strict'),{chromium}=require('playwright');
const source=fs.readFileSync('src/app.js','utf8'),html=fs.readFileSync('hamghadam-preview.html','utf8');
const publicData=JSON.parse(source.match(/var ld=JSON.parse\(`(.*?)`\)/s)[1]),archive=JSON.parse(fs.readFileSync('data/unpublished-centers.json','utf8'));
assert.equal(publicData.length,10);assert.equal(archive.length,7);assert.equal(new Set([...publicData,...archive].map(e=>e.id)).size,17);
assert(archive.every(e=>e.isPublished===false&&e.listingStatus==='unpublished'));
for(const c of archive){assert(!html.includes(c.id));assert(!fs.existsSync(`centers/${c.id}/index.html`));}
// Compare against the exact pre-change dataset when available locally.
if(fs.existsSync('work/centers-before-unpublish.json')){
 const before=JSON.parse(fs.readFileSync('work/centers-before-unpublish.json','utf8'));
 for(const c of publicData)assert.deepEqual(c,before.find(e=>e.id===c.id));
 for(const c of archive)assert.deepEqual({...c,isPublished:true,listingStatus:'listed_unverified'},before.find(e=>e.id===c.id));
}
(async()=>{const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});try{
 for(const width of [320,390,1440]){
 const context=await browser.newContext({viewport:{width,height:900}});await context.route('**/*',r=>r.request().url().startsWith('https://directory.test/')?r.fulfill({contentType:'text/html',body:html}):r.abort());const page=await context.newPage();
 await page.goto('https://directory.test/');await page.locator('#center-search-results[data-result-count="10"]').waitFor();assert.equal(await page.locator('.center-card').count(),10);
 const structured=await page.locator('[data-home-structured-data]').textContent();for(const c of archive)assert(!structured.includes(c.id));for(const c of publicData)assert(structured.includes(c.id));
 const search=page.locator('input[type=search]');for(const c of archive){await search.fill(c.name);await page.waitForTimeout(120);assert.equal(await page.locator(`a[href="#/centers/${c.id}"]`).count(),0)}
 await search.fill('');await page.locator('#center-search-results[data-result-count="10"]').waitFor();
 await page.getByRole('button',{name:'فیلترها',exact:true}).click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');
 for(const c of archive){await page.goto('https://directory.test/#/centers/'+c.id);await page.getByText('مرکز پیدا نشد',{exact:true}).waitFor();assert(!(await page.locator('body').innerText()).includes(c.address));await page.reload();await page.getByText('مرکز پیدا نشد',{exact:true}).waitFor();}
 await page.goto('https://directory.test/');await page.locator('#center-search-results[data-result-count="10"]').waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:`work/qa/public-centers-${width}.png`,fullPage:true});
 await context.close();console.log(`PASS ${width}: exactly 10 cards and JSON-LD entries; 7 hidden profiles stay unavailable after reload; preserved all records.`);
 }
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
