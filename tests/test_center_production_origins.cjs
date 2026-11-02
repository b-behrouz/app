const assert=require('assert/strict');const {createServer,sample}=require('./test_center_server.cjs');
const s=createServer();s.props.ALLOWED_ORIGINS='https://b-behrouz.github.io,https://custom.test';s.props.ALLOW_LOCAL_PREVIEW='false';s.context.setupCenterRequests();
let origins=s.props.ALLOWED_ORIGINS.split(',');for(const host of ['https://b-behrouz.github.io','https://custom.test','https://hamghadamcare.ir','https://www.hamghadamcare.ir'])assert(origins.includes(host));
s.context.enableProductionCenterOrigin();assert.equal(s.props.ALLOWED_ORIGINS.split(',').length,origins.length);
for(const origin of ['https://hamghadamcare.ir','https://www.hamghadamcare.ir'])assert.equal(s.post({...sample(),origin}).result.persisted,true);
for(const origin of ['https://hamghadamcare.ir.evil.test','https://hamghadamcare.ir/path','https://evil.test','null'])assert.equal(s.post({...sample(),origin}).result.code,'INVALID_ORIGIN');
assert.equal(s.props.ALLOW_LOCAL_PREVIEW,'false');console.log('PASS production origin repair: canonical and www allowed, existing custom origins retained, repeated setup idempotent, forged host/path and local preview rejected.');
