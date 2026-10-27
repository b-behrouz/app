const {chromium}=require('playwright');const fs=require('fs'),assert=require('assert/strict');
const {createServer}=require('./test_center_server.cjs');
const endpoint='https://script.google.com/macros/s/TEST_DEPLOYMENT/exec';
fs.mkdirSync('work/qa',{recursive:true});
const source=fs.readFileSync('hamghadam-preview.html','utf8');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {}),args:['--no-sandbox']});
 async function harness(configured=true,width=390){
  const server=createServer();server.props.ALLOWED_ORIGINS='https://hamghadam.test';server.context.setupCenterRequests();
  const context=await browser.newContext({viewport:{width,height:844}});
  let mode='normal',posts=0,acks=new Map();const errors=[];
  await context.route('**/*',async route=>{
   const url=route.request().url();
   if(url.startsWith('https://hamghadam.test'))return route.fulfill({contentType:'text/html',body:source.replace(/const HAMGHADAM_CENTER_ENDPOINT = '[^']*';/,`const HAMGHADAM_CENTER_ENDPOINT = '${configured ? endpoint : ''}';`)});
   if(url===endpoint){
    posts++;const payload=JSON.parse(new URLSearchParams(route.request().postData()).get('payload'));
    const response=mode==='error'?{html:`<script>top.postMessage(${JSON.stringify({channel:'hamghadam-center-v1',nonce:payload.nonce,requestId:payload.requestId,ok:false,persisted:false,code:'SERVER_ERROR'})},'*')</script>`}:server.post(payload);
    acks.set(payload.nonce,{html:response.html,mode,payload});
    return route.fulfill({contentType:'text/html',body:`<iframe src="https://n-test-script.googleusercontent.com/ack/${payload.nonce}"></iframe>`});
   }
   if(url.startsWith('https://n-test-script.googleusercontent.com/ack/')){
    const item=acks.get(url.split('/').pop());
    let body=item.html;
    if(item.mode==='drop')body='<p>Response intentionally lost</p>';
    if(item.mode==='delay')body=`<script>top.postMessage(${JSON.stringify({channel:'hamghadam-center-v1',nonce:'WRONG_NONCE',requestId:item.payload.requestId,ok:true,persisted:true})},'*'); setTimeout(()=>{${item.html.match(/<script>(.*)<\/script>/s)[1]}},800)</script>`;
    return route.fulfill({contentType:'text/html',body});
   }
   return route.abort();
  });
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('https://hamghadam.test/#/introduce-center');await page.locator('#center-referral-name').waitFor();
  const fill=async()=>{for(const [name,value] of Object.entries({name:'مرکز آزمایشی',phone:'۰۵۱۳۸۴۵۶۷۸۹',area:'مشهد',services:'پانسمان آزمایشی'}))await page.locator('[name="'+name+'"]').fill(value)};
  return {page,context,server,fill,errors,setMode:m=>mode=m,posts:()=>posts,rows:()=>server.tabs.get('معرفی مراکز هم‌قدم').rows};
 }
 // Preserve original validation and prevent network calls on invalid input.
 let h=await harness();let p=h.page;await p.locator('button[type=submit]').click();await p.getByText('نام مرکز خدمات پرستاری را وارد کنید.',{exact:true}).waitFor();assert.equal(h.posts(),0);
 await h.fill();h.setMode('delay');
 await p.locator('form.center-referral-form').evaluate(form=>{form.requestSubmit();form.requestSubmit()});
 await p.getByRole('button',{name:'در حال ثبت اطلاعات…'}).waitFor();assert(await p.locator('[name=name]').isDisabled());
 assert.equal(await p.getByText('اطلاعات مرکز با موفقیت ثبت شد و در انتظار بررسی است.',{exact:true}).count(),0);
 await p.getByText('اطلاعات مرکز با موفقیت ثبت شد و در انتظار بررسی است.',{exact:true}).waitFor();
 assert.equal(h.posts(),1);assert.equal(h.rows().length,2);assert(await p.getByRole('button',{name:'اطلاعات ثبت شد',exact:true}).isDisabled());
 assert.equal(await p.locator('iframe[name^=center-]').count(),0);assert.equal(await p.locator('[name=name]').inputValue(),'مرکز آزمایشی');
 console.log('PASS browser: unchanged validation; real cross-origin form POST; nested iframe acknowledgment; wrong nonce ignored; pending fields/button locked; double submit blocked; success only after persistence; cleanup.');
 assert.deepEqual(h.errors,[]);await h.context.close();
 // A write completed but its acknowledgment was lost. Retry must use the same ID.
 h=await harness();p=h.page;await h.fill();await p.clock.install();h.setMode('drop');await p.locator('button[type=submit]').click();
 await p.waitForFunction(()=>document.querySelector('iframe[name^=center-]')?.contentWindow!=null);await p.waitForTimeout(200);
 assert.equal(h.rows().length,2);await p.clock.fastForward(46000);
 await p.getByText(/تأیید ثبت دریافت نشد/).waitFor();assert.equal(await p.locator('[name=phone]').inputValue(),'۰۵۱۳۸۴۵۶۷۸۹');
 assert(!(await p.locator('button[type=submit]').isDisabled()));h.setMode('normal');await p.locator('button[type=submit]').click();await p.getByText(/اطلاعات مرکز با موفقیت ثبت شد/).waitFor();assert.equal(h.posts(),2);assert.equal(h.rows().length,2);
 console.log('PASS browser: timeout retains all values; retry uses same ID and produces no duplicate row.');await h.context.close();
 // Explicit error is never displayed as success.
 h=await harness();p=h.page;await h.fill();h.setMode('error');await p.locator('button[type=submit]').click();await p.getByText(/سرویس ثبت اطلاعات با خطا روبه‌رو شد/).waitFor();assert.equal(h.rows().length,1);assert.equal(await p.locator('[name=area]').inputValue(),'مشهد');console.log('PASS browser: server error preserves form and allows retry.');await h.context.close();
 h=await harness(false);p=h.page;await h.fill();await p.locator('button[type=submit]').click();await p.getByText(/اتصال ثبت اطلاعات هنوز پیکربندی نشده/).waitFor();assert.equal(h.posts(),0);console.log('PASS browser: missing deployment cannot report success.');await h.context.close();
 // Server rejection must be specific and must not show a success or clear the form.
 h=await harness();p=h.page;await h.fill();h.server.props.ALLOWED_ORIGINS='https://other.test';
 await p.locator('button[type=submit]').click();await p.getByText(/INVALID_ORIGIN/).waitFor();
 assert.equal(h.rows().length,1);assert.equal(await p.locator('[name=name]').inputValue(),'مرکز آزمایشی');
 console.log('PASS browser: rejected origin is reported explicitly without saving or clearing values.');await h.context.close();
 h=await harness();p=h.page;await h.fill();await p.evaluate(()=>Object.defineProperty(window,'crypto',{value:{},configurable:true}));
 await p.locator('button[type=submit]').click();await p.getByText(/BROWSER_UNSUPPORTED/).waitFor();
 assert.equal(h.posts(),0);assert.equal(await p.locator('[name=area]').inputValue(),'مشهد');
 console.log('PASS browser: unsupported crypto is detected before any send and form values remain intact.');await h.context.close();
 // Visual and field-contract comparison at both viewport sizes.
 for(const [name,width] of [['mobile',390],['desktop',1440]]){
  h=await harness(true,width);p=h.page;await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
  const actual=await p.locator('.center-referral-form input,.center-referral-form textarea').evaluateAll(es=>es.map(e=>({name:e.name,type:e.type,maxLength:e.maxLength,required:e.required,placeholder:e.placeholder})));
  const expected=[
   {name:'name',type:'text',maxLength:160,required:true,placeholder:''},
   {name:'phone',type:'tel',maxLength:32,required:true,placeholder:''},
   {name:'area',type:'text',maxLength:200,required:true,placeholder:''},
   {name:'services',type:'textarea',maxLength:3000,required:false,placeholder:''}
  ];
  assert.deepEqual(actual,expected);assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await p.screenshot({path:`work/qa/${name}-form.png`,fullPage:true});console.log('PASS '+name+': original four fields, types, lengths and required flags preserved; no horizontal overflow.');await h.context.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
