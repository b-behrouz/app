const {chromium}=require('playwright'),fs=require('fs'),assert=require('assert/strict');
(async()=>{const b=await chromium.launch({...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {}),args:['--no-sandbox']});try{
 const fp=await b.newPage();try{await fp.goto('file://'+require('path').resolve('hamghadam-preview.html')+'');console.log('FILE OK')}catch(e){console.log('FILE TEST BLOCKED:',e.message.split('\n')[0])}await fp.close();
 for(const width of [320,390,1440]){
 const c=await b.newContext({viewport:{width,height:900}});await c.route('**/*',r=>r.request().url().startsWith('https://preview.test/')?r.fulfill({contentType:'text/html',body:fs.readFileSync('hamghadam-preview.html','utf8')}):r.abort());const p=await c.newPage();
 await p.goto('https://preview.test/');await p.locator('.hero-heading').waitFor();assert.equal(await p.locator('.hero-eyebrow').count(),0);assert.equal(await p.locator('.site-header-brand-row').count(),1);
 const input=p.locator('input').first();await input.focus();await p.waitForTimeout(300);const focus=await input.evaluate(e=>{let s=getComputedStyle(e);return [s.borderTopWidth,s.borderTopColor,s.boxShadow,s.outlineStyle]});assert.deepEqual(focus,['1px','rgb(145, 181, 223)','none','none']);
 for(const path of ['feedback','introduce-center']){
 await p.goto('https://preview.test/#/'+path);await p.locator('.site-header-compact').waitFor();assert.equal(await p.locator('.site-header-brand-row').count(),0);assert.equal(await p.locator('.site-header-page-row').evaluate(e=>getComputedStyle(e).borderTopWidth),'0px');
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 if(path==='feedback'){
 const rhythm=await p.locator('.feedback-question').evaluateAll(es=>es.map(e=>({border:getComputedStyle(e).borderTopWidth,rect:e.getBoundingClientRect().toJSON()})));
 assert(rhythm.every(e=>e.border==='0px'));assert(rhythm[1].rect.top-rhythm[0].rect.bottom>=30);assert(rhythm[2].rect.top-rhythm[1].rect.bottom>=30);
 const marker=await p.locator('.hamghadam-bottom-nav a[aria-current=page]').evaluate(e=>{const l=getComputedStyle(e,'::after'),s=getComputedStyle(e),icon=e.querySelector('svg').getBoundingClientRect();return {w:l.width,h:l.height,top:parseFloat(l.top)+e.getBoundingClientRect().top,iconTop:icon.top,color:s.color};});
 assert.equal(marker.w,'12px');assert.equal(marker.h,'2px');assert(marker.top+2<marker.iconTop);assert.equal(marker.color,'rgb(57, 118, 184)');

 assert.equal(await p.locator('.hamghadam-form-alert[data-status=info]').count(),0);const radios=p.getByRole('radio');assert.equal(await radios.count(),5);const dims=await radios.first().evaluate(e=>{let s=getComputedStyle(e);return [e.getBoundingClientRect().height,s.paddingTop,s.paddingBottom]});assert.deepEqual(dims,[88,'16px','16px']);await radios.nth(3).click();assert.equal(await radios.nth(3).getAttribute('aria-checked'),'true');
 await p.locator('#feedback-notes').focus();assert.equal(await p.locator('#feedback-notes').evaluate(e=>getComputedStyle(e).boxShadow),'none');
 }else{
 const notice=p.locator('#center-submission-notice');assert.equal(await notice.count(),1);assert(await notice.evaluate(e=>!!(e.compareDocumentPosition(document.querySelector('.center-referral-form'))&Node.DOCUMENT_POSITION_FOLLOWING)));assert.equal(await p.locator('form').getAttribute('aria-describedby'),'center-submission-notice');
 await p.locator('button[type=submit]').click();await p.locator('input[aria-invalid=true]').first().waitFor();const invalid=p.locator('input[aria-invalid=true]').first();await invalid.focus();assert.notEqual(await invalid.evaluate(e=>getComputedStyle(e).borderTopColor),'rgb(145, 181, 223)');
 }
 const active=p.locator('.hamghadam-bottom-nav a[aria-current=page]');const style=await active.evaluate(e=>{let s=getComputedStyle(e),l=getComputedStyle(e,'::after');return [s.backgroundColor,s.fontWeight,l.height,l.position]});assert.deepEqual(style,['rgba(0, 0, 0, 0)','500','2px','absolute']);
 await p.evaluate(()=>{document.activeElement.blur();window.scrollTo(0,0)});await p.screenshot({path:`work/qa/refinement-${width}-${path}.png`,fullPage:true});
 }
 await p.getByRole('button',{name:'پشتیبانی',exact:true}).click();const support=p.locator('.hamghadam-bottom-nav button[aria-expanded=true]');assert.equal(await support.evaluate(e=>getComputedStyle(e,'::after').height),'2px');await c.close();console.log('PASS refinement layout',width);
 }
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
