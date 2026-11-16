const assert=require('assert/strict');const {createServer,sample}=require('./test_center_server.cjs');
const s=createServer();s.props.ALLOWED_ORIGINS='https://b-behrouz.github.io,https://custom.test';s.props.ALLOW_LOCAL_PREVIEW='false';s.context.setupCenterRequests();
let origins=s.props.ALLOWED_ORIGINS.split(',');for(const host of ['https://b-behrouz.github.io','https://custom.test','https://rahnamasalamat.ir','https://www.rahnamasalamat.ir','https://hamghadamcare.ir','https://www.hamghadamcare.ir'])assert(origins.includes(host));
s.context.enableProductionCenterOrigin();assert.equal(s.props.ALLOWED_ORIGINS.split(',').length,origins.length);
for(const origin of ['https://rahnamasalamat.ir','https://www.rahnamasalamat.ir','https://hamghadamcare.ir','https://www.hamghadamcare.ir'])assert.equal(s.post({...sample(),origin}).result.persisted,true);
for(const origin of ['https://rahnamasalamat.ir.evil.test','https://www.rahnamasalamat.ir.evil.test','https://rahnamasalamat.ir/path','https://rahnamasalamat.ir/','https://rahnamasalamat.ir?x=1','https://rahnamasalamat.ir#x','http://rahnamasalamat.ir','https://hamghadamcare.ir.evil.test','https://hamghadamcare.ir/path','https://evil.test','*','null'])assert.equal(s.post({...sample(),origin}).result.code,'INVALID_ORIGIN');
// Simulate the old active service policy. Changing properties must take effect
// on the next POST without rerunning setup or changing deployment/sheet IDs.
const active=createServer();active.context.setupCenterRequests();
active.props.ALLOWED_ORIGINS='https://hamghadamcare.ir';
const request={...sample(),origin:'https://rahnamasalamat.ir'};
const rows=active.tabs.get('معرفی مراکز هم‌قدم').rows;
assert.equal(active.post(request).result.code,'INVALID_ORIGIN');assert.equal(rows.length,1);
active.context.enableProductionCenterOrigin();
assert(active.post(request).result.persisted);assert.equal(rows.length,2);
assert(active.post({...request,nonce:sample().nonce}).result.persisted);assert.equal(rows.length,2);
assert.equal(rows[1][3],request.name);assert.equal(rows[1][4],request.phone);
active.state.failWrite=true;
assert.equal(active.post({...sample(),origin:request.origin}).result.persisted,false);
active.state.failWrite=false;
assert.equal(active.post({...sample(),origin:request.origin,phone:'123'}).result.code,'VALIDATION_ERROR');
assert.equal(rows.length,2);
assert.equal(s.props.ALLOW_LOCAL_PREVIEW,'false');console.log('PASS production origin repair: canonical and www allowed, existing custom origins retained, repeated setup idempotent, forged host/path and local preview rejected.');
