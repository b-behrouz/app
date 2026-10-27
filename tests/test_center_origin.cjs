const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync('src/app.js','utf8');
const start=source.indexOf('function HamghadamCenterOrigin()');
const end=source.indexOf('function HamghadamPostCenter(payload)',start);
function origin(protocol,value){const c=vm.createContext({location:{protocol,origin:value}});vm.runInContext(source.slice(start,end),c);return c.HamghadamCenterOrigin()}
assert.equal(origin('content:','content://org.telegram.messenger'),'null');assert.equal(origin('content:','null'),'null');assert.equal(origin('blob:','null'),'null');assert.throws(()=>origin('custom:','custom://host'),/UNSUPPORTED_ORIGIN/);assert.equal(origin('file:','file://'),'null');assert.equal(origin('file:','null'),'null');
assert.equal(origin('https:','https://b-behrouz.github.io'),'https://b-behrouz.github.io');
const c=vm.createContext({});vm.runInContext(source.slice(start,end),c);
assert(c.HamghadamCenterSubmissionError(new Error('INVALID_ORIGIN')).includes('(INVALID_ORIGIN)'));
assert(c.HamghadamCenterSubmissionError(new Error('TIMEOUT')).includes('(TIMEOUT)'));
assert(!c.HamghadamCenterSubmissionError(new Error('private detail')).includes('private detail'));
console.log('PASS: local origin normalization and safe actionable errors.');
