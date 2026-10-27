const {chromium}=require('playwright'),fs=require('fs'),assert=require('assert/strict');
const {createServer}=require('./test_center_server.cjs');
const html=fs.readFileSync('hamghadam-preview.html','utf8');
const config=html.match(/var ww=\{spreadsheetId:`([^`]+)`,endpoint:`([^`]+)`/);
const endpoint=html.match(/const HAMGHADAM_CENTER_ENDPOINT = '([^']+)';/)[1];
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 try{
  for(const [size,width,height] of [['small',320,800],['mobile',390,900],['desktop',1440,1000]]){
   const context=await browser.newContext({viewport:{width,height}});
   const server=createServer();server.props.ALLOWED_ORIGINS='https://alerts.test';server.context.setupCenterRequests();
   let errorMode=true,posts=0;
   await context.route('**/*',async route=>{
    const request=route.request(),url=request.url();
    if(url.startsWith('https://alerts.test/'))return route.fulfill({contentType:'text/html',body:html});
    if(request.method()==='POST'&&url===config[2]){
     posts++;const payload=JSON.parse(new URLSearchParams(request.postData()).get('payload'));
     await new Promise(resolve=>setTimeout(resolve,500));
     return route.fulfill({status:errorMode?503:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({ok:!errorMode,id:payload.id,spreadsheetId:config[1]})});
    }
    if(request.method()==='POST'&&url===endpoint){
     posts++;const payload=JSON.parse(new URLSearchParams(request.postData()).get('payload'));
     if(errorMode){server.props.ALLOWED_ORIGINS='https://other.test'}else{server.props.ALLOWED_ORIGINS='https://alerts.test'}
     const reply=server.post(payload);await new Promise(resolve=>setTimeout(resolve,500));
     return route.fulfill({contentType:'text/html',body:reply.html});
    }
    return route.abort();
   });
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   async function inspect(variant,screenshot){
    const alert=page.locator(`.hamghadam-form-alert[data-status=${variant}]`).first();await alert.waitFor();await alert.scrollIntoViewIfNeeded();
    assert.equal(await alert.getAttribute('role'),variant==='error'?'alert':'status');
    assert.equal(await alert.locator(':scope > svg[aria-hidden=true]').count(),1);
    assert.equal(await alert.locator('[data-slot=alert-description]').count(),1);
    const bounds=await alert.evaluate(e=>{const r=e.getBoundingClientRect(),svg=e.querySelector('svg').getBoundingClientRect(),text=e.querySelector('[data-slot=alert-description]').getBoundingClientRect();return {x:r.x,right:r.right,width:r.width,iconX:svg.x,textRight:text.right,direction:getComputedStyle(e).direction,border:getComputedStyle(e).borderTopWidth}});
    assert(bounds.x>=0&&bounds.right<=width,'Alert overflow');assert(bounds.iconX>=bounds.textRight,'Icon should be at RTL start');assert.equal(bounds.direction,'rtl');assert.equal(bounds.border,'1px');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    if(screenshot){fs.mkdirSync('work/qa/alerts',{recursive:true});await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:`work/qa/alerts/${size}-${screenshot}.png`});}
   }
   await page.goto('https://alerts.test/#/introduce-center');await inspect('info','center-info');
   await page.locator('.center-referral-form button[type=submit]').click();assert.equal(posts,0);await page.getByText('نام مرکز خدمات پرستاری را وارد کنید.',{exact:true}).waitFor();
   for(const [name,value] of Object.entries({name:'مرکز آزمایشی',phone:'۰۵۱۳۸۴۵۶۷۸۹',area:'مشهد',services:'پانسمان آزمایشی'}))await page.locator('[name='+name+']').fill(value);
   await page.locator('.center-referral-form button[type=submit]').click();await inspect('error','center-error');await page.getByText(/INVALID_ORIGIN/).waitFor();
   assert.equal(await page.locator('[name=name]').inputValue(),'مرکز آزمایشی');assert.equal(server.tabs.get('معرفی مراکز هم‌قدم').rows.length,1);
   errorMode=false;await page.locator('.center-referral-form button[type=submit]').click();
   assert.equal(await page.locator('.hamghadam-form-alert[data-status=success]').count(),0);
   await inspect('success','center-success');assert.equal(server.tabs.get('معرفی مراکز هم‌قدم').rows.length,2);
   await page.goto('https://alerts.test/#/feedback');assert.equal(await page.locator('.hamghadam-form-alert[data-status=info]').count(),0);
   const before=posts;await page.getByRole('button',{name:'ارسال نظر',exact:true}).click();assert.equal(posts,before);await page.getByText('لطفاً تجربه کلی‌تون رو انتخاب کنید.',{exact:true}).waitFor();
   await page.getByRole('radio').nth(3).click();await page.locator('#feedback-notes').fill('بازخورد آزمایشی');errorMode=true;
   await page.getByRole('button',{name:'ارسال نظر',exact:true}).click();await inspect('error','feedback-error');assert.equal(await page.locator('#feedback-notes').inputValue(),'بازخورد آزمایشی');
   errorMode=false;await page.getByRole('button',{name:'ارسال نظر',exact:true}).click();assert.equal(await page.locator('.hamghadam-form-alert[data-status=success]').count(),0);
   await inspect('success','feedback-success');await page.getByText('بازخورد شما با موفقیت ارسال شد.',{exact:true}).waitFor();
   assert.equal(await page.locator('.hamghadam-form-alert [data-slot=alert-title]').innerText(),'ممنون که نظرتون رو با ما در میون گذاشتید 💙');
   assert.deepEqual(errors,[]);await context.close();
   console.log(`PASS ${size}: both forms share RTL shadcn Alerts for info/error/success; validation, retained values and success-after-ack preserved.`);
  }
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
