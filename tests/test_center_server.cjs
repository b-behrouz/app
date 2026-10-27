const vm=require('vm'),fs=require('fs'),crypto=require('crypto'),assert=require('assert/strict');
function createServer(){
 const tabs=new Map([['داده قبلی',{rows:[['قدیمی'],['حفظ شود']]}]]), props={ALLOWED_ORIGINS:'http://hamghadam.test,https://hamghadamcare.ir'},state={failWrite:false,failRead:false,locked:false,flushes:0};
 class Range {
  constructor(sheet,r,c,n=1,m=1){Object.assign(this,{sheet,r,c,n,m})}
  setValues(rows){if(state.failWrite)throw Error('write failed');rows.forEach((row,i)=>row.forEach((v,j)=>{const dest=this.sheet.rows[this.r+i-1] ||= [];dest[this.c+j-1]=typeof v==='string'&&v.startsWith("'")?v.slice(1):v}));return this}
  getValues(){if(state.failRead)throw Error('read failed');return Array.from({length:this.n},(_,i)=>Array.from({length:this.m},(_,j)=>this.sheet.rows[this.r+i-1]?.[this.c+j-1]??''))}
  getValue(){return this.getValues()[0][0]}
  setNumberFormat(){return this}
  getRow(){return this.r}
  createTextFinder(value){const find=()=>this.getValues().flatMap((row,i)=>row[0]===value?[new Range(this.sheet,this.r+i,this.c)]:[]);return {matchEntireCell(){return this},useRegularExpression(){return this},findNext(){return find()[0]||null},findAll(){return find()}}}
 }
 function sheet(name){const raw=tabs.get(name);if(!raw)return null;return {getRange:(...args)=>new Range(raw,...args),getLastRow:()=>raw.rows.length,setFrozenRows:()=>{}}}
 const book={getSheetByName:sheet,insertSheet(name){tabs.set(name,{rows:[]});return sheet(name)}};
 const context=vm.createContext({console,Date,JSON,Error,SpreadsheetApp:{openById:id=>{assert.equal(id,'1Z6H-1whyeoH0XNDzvY1u88dsOr2ltnVCLZQ_ukBHatc');return book},flush(){state.flushes++}},PropertiesService:{getScriptProperties:()=>({getProperty:k=>props[k]||null,setProperty:(k,v)=>props[k]=v})},LockService:{getScriptLock:()=>({waitLock(){assert(!state.locked);state.locked=true},tryLock(){if(state.locked)return false;state.locked=true;return true},releaseLock(){state.locked=false}})},Utilities:{getUuid:()=>crypto.randomUUID(),DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'},computeDigest:(a,s)=>Array.from(crypto.createHash('sha256').update(s).digest())},HtmlService:{XFrameOptionsMode:{ALLOWALL:'allow'},createHtmlOutput:html=>({html,setXFrameOptionsMode(){return this},getContent(){return html}})}});
 vm.runInContext(fs.readFileSync('google-sheets/Code.gs','utf8'),context);
 function post(data){const output=context.doPost({parameter:{payload:JSON.stringify(data)}});const match=output.html.match(/postMessage\((.*),"(?:[^"]*)"\);<\/script>/);return {html:output.html,result:JSON.parse(match[1])}}
 return {context,post,tabs,props,state};
}
function sample(){return {requestId:crypto.randomUUID(),nonce:crypto.randomUUID(),origin:'http://hamghadam.test',name:'مرکز نمونه',phone:'۰۵۱۳۸۴۵۶۷۸۹',area:'مشهد',services:'پانسمان'}}
function tests(){
 const server=createServer(); const {context,post,tabs,state}=server;
 context.setupCenterRequests();const before=JSON.stringify(tabs.get('داده قبلی'));
 const d=sample();let r=post(d).result;assert(r.ok&&r.persisted);assert(!state.locked);assert.equal(state.flushes,2);
 let rows=tabs.get('معرفی مراکز هم‌قدم').rows;assert.equal(rows.length,2);assert.equal(rows[1][2],'در انتظار بررسی');assert(!isNaN(Date.parse(rows[1][1])));assert.equal(rows[1][4],d.phone);
 assert(post({...d,nonce:crypto.randomUUID()}).result.persisted);assert.equal(rows.length,2);
 assert.equal(post({...d,name:'مرکز دیگر'}).result.code,'ID_CONFLICT');assert.equal(rows.length,2);
 for(const patch of [{name:''},{area:' '},{phone:'123'},{services:'x'.repeat(3001)},{requestId:'bad'},{nonce:'bad'},{origin:'https://other.test'}]){assert(!post({...sample(),...patch}).result.ok);assert.equal(rows.length,2)}
 state.failWrite=true;assert(!post(sample()).result.persisted);state.failWrite=false;assert(!state.locked);
 const malicious=sample();malicious.name='=IMPORTXML("https://example.test","//a")';assert(post(malicious).result.persisted);assert.equal(rows[2][3],malicious.name);
 state.locked=true;assert.equal(post(sample()).result.code,'BUSY');state.locked=false;
 const savedHeader=rows[0][0];rows[0][0]='wrong';assert.equal(post(sample()).result.code,'HEADER_MISMATCH');assert.equal(rows[0][0],'wrong');rows[0][0]=savedHeader;
 assert.equal(JSON.stringify(tabs.get('داده قبلی')),before);
 const local=sample();local.origin='null';assert.equal(post(local).result.code,'INVALID_ORIGIN');server.props.ALLOW_LOCAL_PREVIEW='true';assert(post(local).result.ok);
 const quota=createServer();quota.context.setupCenterRequests();const saved=sample();assert(quota.post(saved).result.persisted);
 quota.props.CENTER_RATE_WINDOW=JSON.stringify({start:Date.now(),count:30});
 assert.equal(quota.post(sample()).result.code,'RATE_LIMITED');assert(quota.post(saved).result.persisted);
 assert.equal(quota.tabs.get('معرفی مراکز هم‌قدم').rows.length,2);
 for(const origin of ['content://org.telegram.messenger','file://','https://hamghadam.test/path','*',null])assert.equal(quota.post({...sample(),origin}).result.code,'INVALID_ORIGIN');
 quota.props.CENTER_RATE_WINDOW=JSON.stringify({start:Date.now()-61000,count:30});assert(quota.post(sample()).result.persisted);
 assert.equal(post({...sample(),origin:'null'}).result.serviceVersion,'2026-10-27-local-origin-v2');
 context.testCenterRequestRoundTrip();
 console.log('PASS server: append, timestamp, status, persistent deduplication, conflicts, validation, formula escaping, write failure, locking, headers, unchanged old data, local opt-in.');
}
if(require.main===module)tests();module.exports={createServer,sample};
