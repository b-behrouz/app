const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const manifest=JSON.parse(fs.readFileSync('.pages-manifest.json','utf8'));
const base='https://pages.test'+manifest.base_path;
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 try{
  for(const [name,width] of [['mobile',390],['desktop',1440]]){
   const context=await browser.newContext({viewport:{width,height:900}});const errors=[],statusCodes=[];
   await context.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.origin!=='https://pages.test')return route.abort();
    assert(u.pathname.startsWith(manifest.base_path),'Navigation escaped /app/');
    const relative=decodeURIComponent(u.pathname.slice(manifest.base_path.length));
    let file=path.resolve(relative||'.');
    assert(file.startsWith(process.cwd()));
    if(fs.existsSync(file)&&fs.statSync(file).isDirectory()){
     if(!u.pathname.endsWith('/'))return route.fulfill({status:301,headers:{location:u.pathname+'/'},body:''});
     file=path.join(file,'index.html');
    }
    let status=200;
    if(!fs.existsSync(file)){file=path.resolve('404.html');status=404}
    statusCodes.push(status);return route.fulfill({status,contentType:'text/html; charset=utf-8',body:fs.readFileSync(file)});
   });
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.locator('.hero-gradient').waitFor();
   assert(!(await page.locator('body').innerText()).includes('نسخهٔ مستقل محلی'));
   const originalCount=Number(await page.locator('#center-search-results').getAttribute('data-result-count'));
   assert(originalCount>0);
   await page.locator('input[type=search]').fill('zzzznonexistent');await page.waitForFunction(()=>document.querySelector('#center-search-results')?.dataset.resultCount==='0');
   await page.locator('input[type=search]').fill('');await page.waitForFunction(n=>Number(document.querySelector('#center-search-results')?.dataset.resultCount)===n,originalCount);
   await page.getByRole('button',{name:'فیلترها',exact:true}).click();let dialog=page.getByRole('dialog');
   await dialog.getByText('پانسمان',{exact:true}).click();await dialog.getByRole('button',{name:'نمایش نتایج',exact:true}).click();
   await page.waitForFunction(n=>{const count=Number(document.querySelector('#center-search-results')?.dataset.resultCount);return count>0&&count<n},originalCount);
   await page.getByRole('button',{name:'فیلترها',exact:true}).click();dialog=page.getByRole('dialog');
   await dialog.getByRole('button',{name:'پاک کردن فیلترها',exact:true}).click();await dialog.getByRole('button',{name:'نمایش نتایج',exact:true}).click();
   await page.waitForFunction(n=>Number(document.querySelector('#center-search-results')?.dataset.resultCount)===n,originalCount);
   // Existing HashRouter URLs remain under /app/ and survive a refresh.
   await page.locator('a[href^="#/centers/"]').first().click();assert(page.url().startsWith(base+'#/centers/'));
   await page.locator('.app-shell.profile-route').waitFor();await page.reload();await page.locator('.app-shell.profile-route').waitFor();
   const gallery=page.getByRole('button',{name:/نمایش کامل تصویر ثبت‌شده/});assert(await gallery.count()>0);await gallery.first().click();
   await page.getByRole('region',{name:'گالری بزرگ تصاویر مرکز'}).waitFor();await page.keyboard.press('ArrowLeft');await page.keyboard.press('Escape');
   // Clean direct links have real directory indexes; no 404 fallback is needed.
   for(const route of ['/centers/ibn-sina-mashhad','/need','/feedback','/introduce-center']){
    await page.goto(base+route.slice(1)+'/');await page.waitForURL(base+'#'+route);await page.reload();
    assert(page.url().startsWith(base+'#'+route));
    if(route==='/feedback')await page.locator('.feedback-form').waitFor();
    if(route==='/introduce-center'){
     await page.locator('#center-referral-name').waitFor();
     await page.locator('.center-referral-form button[type=submit]').click();await page.getByText('نام مرکز خدمات پرستاری را وارد کنید.',{exact:true}).waitFor();
    }
   }
   await page.goto(base);await page.getByRole('button',{name:'پشتیبانی',exact:true}).click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   assert.deepEqual(errors,[]);assert(!statusCodes.includes(404),'Known routes returned 404');
   await page.evaluate(()=>document.fonts.ready);fs.mkdirSync('work/qa',{recursive:true});await page.screenshot({path:`work/qa/${name}-pages.png`});
   console.log(`PASS ${name}: /app/ homepage, search, applied filters, profile/gallery, forms, support, clean deep links and reload; no known-route 404s.`);
   await context.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
