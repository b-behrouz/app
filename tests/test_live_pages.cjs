// Public-site verification only: no interception, local fixtures, credentials or form submissions.
const {chromium}=require('playwright');
const fs=require('fs'),crypto=require('crypto'),assert=require('assert/strict');
const base='https://b-behrouz.github.io/app/';
const digest=data=>crypto.createHash('sha256').update(data).digest('hex');
const expected=digest(fs.readFileSync('index.html'));
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 const report={url:base,expectedSha256:expected,checks:[],commit:process.env.GITHUB_SHA||null};
 try{
  const request=await browser.newContext();
  const deadline=Date.now()+300000;
  let ready=false,last='no response';
  while(Date.now()<deadline){
   try{
    const response=await request.request.get(base,{headers:{'Cache-Control':'no-cache'},timeout:20000});
    const observed=digest(await response.body());
    last=`HTTP ${response.status()}, SHA256 ${observed}`;
    if(response.status()===200&&observed===expected){ready=true;report.observedSha256=observed;report.httpStatus=200;break}
   }catch(error){last=error.message.split('\n')[0]}
   console.log('Waiting for approved Pages output:',last);
   await new Promise(resolve=>setTimeout(resolve,10000));
  }
  assert(ready,'Live response did not match the approved HTML: '+last);
  await request.close();
  for(const [name,width] of [['mobile',390],['desktop',1440]]){
   const context=await browser.newContext({viewport:{width,height:900}});const page=await context.newPage();
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   const response=await page.goto(base,{waitUntil:'load'});assert.equal(response.status(),200);
   await page.locator('.hero-gradient').waitFor();
   assert(!(await page.locator('body').innerText()).includes('نسخهٔ مستقل محلی'));
   const search=page.locator('input[type=search]');await search.fill('zzzznonexistent');
   await page.waitForFunction(()=>document.querySelector('#center-search-results')?.dataset.resultCount==='0');
   await search.fill('');await page.waitForFunction(()=>Number(document.querySelector('#center-search-results')?.dataset.resultCount)>0);
   await page.getByRole('button',{name:'فیلترها',exact:true}).click();
   await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');
   await page.goto(base+'centers/ibn-sina-mashhad/');
   await page.waitForURL(base+'#/centers/ibn-sina-mashhad');await page.locator('.app-shell.profile-route').waitFor();
   await page.reload();await page.locator('.app-shell.profile-route').waitFor();
   await page.getByRole('button',{name:/نمایش کامل تصویر ثبت‌شده/}).first().click();
   await page.getByRole('region',{name:'گالری بزرگ تصاویر مرکز'}).waitFor();await page.keyboard.press('Escape');
   await page.goto(base+'introduce-center/');await page.waitForURL(base+'#/introduce-center');
   await page.locator('#center-referral-name').waitFor();
   await page.locator('.center-referral-form button[type=submit]').click();
   await page.getByText('نام مرکز خدمات پرستاری را وارد کنید.',{exact:true}).waitFor();
   await page.goto(base+'feedback/');await page.waitForURL(base+'#/feedback');await page.locator('.feedback-form').waitFor();
   await page.goto(base);await page.getByRole('button',{name:'پشتیبانی',exact:true}).click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Escape');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(errors,[]);
   await page.evaluate(()=>document.fonts.ready);fs.mkdirSync('work/live-qa',{recursive:true});
   await page.screenshot({path:`work/live-qa/${name}.png`});
   report.checks.push({viewport:name,passed:true,ui:true,search:true,filterPanel:true,profile:true,gallery:true,forms:true,support:true,deepLinkAndRefresh:true});
   console.log(`PASS LIVE ${name}: actual public URL rendered Hamghadam, search, filter panel, profile/gallery, form validation, feedback, support and deep-link reload.`);
   await context.close();
  }
  fs.writeFileSync('work/live-qa/report.json',JSON.stringify(report,null,2)+'\n');
  console.log('LIVE VERIFIED:',base,'SHA256',expected);
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
