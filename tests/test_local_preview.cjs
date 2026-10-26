const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path'),fs=require('fs'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 try{
  for(const [name,width] of [['mobile',390],['desktop',1440]]){
   const context=await browser.newContext({viewport:{width,height:900},offline:true});
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   const file=pathToFileURL(path.resolve('hamghadam-preview.html')).href;
   try{await page.goto(file)}catch(error){
    if(error.message.includes('ERR_BLOCKED_BY_ADMINISTRATOR'))throw Error('FILE_QA_BLOCKED: managed browser policy forbids file://; actual local rendering is NOT verified.');
    throw error;
   }
   assert(page.url().startsWith('file://'));
   await page.locator('.hero-gradient').waitFor();await page.evaluate(()=>document.fonts.ready);
   assert.equal(await page.locator('.hero-heading').innerText(),'مراقبت مناسب\nاز شناخت نیاز شروع می‌شود.');
   const search=page.locator('input[type=search]');await search.fill('zzzznonexistent');
   await page.waitForFunction(()=>document.querySelector('#center-search-results')?.getAttribute('data-result-count')==='0');
   await search.fill('');await page.waitForFunction(()=>Number(document.querySelector('#center-search-results')?.getAttribute('data-result-count'))>0);
   await page.getByRole('button',{name:'فیلترها',exact:true}).click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');
   await page.locator('a[href^="#/centers/"]').first().click();await page.waitForURL(/#\/centers\//);await page.getByText('معرفی مرکز',{exact:true}).first().waitFor();
   await page.goto(file+'#/introduce-center');await page.locator('#center-referral-name').waitFor();
   await page.locator('.center-referral-form button[type=submit]').click();await page.getByText('نام مرکز خدمات پرستاری را وارد کنید.',{exact:true}).waitFor();
   await page.goto(file+'#/feedback');await page.locator('.feedback-form').waitFor();
   await page.goto(file);await page.getByRole('button',{name:'پشتیبانی',exact:true}).click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   assert.deepEqual(errors,[]);
   fs.mkdirSync('work/qa',{recursive:true});await page.screenshot({path:`work/qa/${name}-local.png`});
   console.log(`PASS ${name}: actual file:// offline UI, search, filter, profile, forms and support panel.`);
   await context.close();
  }
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exit(1)});
