/** Google Apps Script V8. Bound to, or authorized to edit, the target spreadsheet. */
const CENTER_SPREADSHEET_ID = '1Z6H-1whyeoH0XNDzvY1u88dsOr2ltnVCLZQ_ukBHatc';
const CENTER_TAB = 'معرفی مراکز هم‌قدم';
const CENTER_HEADERS = ['شناسه درخواست', 'زمان ثبت (UTC)', 'وضعیت', 'نام مرکز خدمات پرستاری', 'شماره تماس مرکز', 'شهر یا محدوده فعالیت', 'توضیحات خدمات مرکز', 'اثر انگشت درخواست'];

function setupCenterRequests() {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const book = SpreadsheetApp.openById(CENTER_SPREADSHEET_ID);
    let sheet = book.getSheetByName(CENTER_TAB);
    if (!sheet) sheet = book.insertSheet(CENTER_TAB);
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, CENTER_HEADERS.length).setValues([CENTER_HEADERS]);
      sheet.setFrozenRows(1);
      SpreadsheetApp.flush();
    }
    assertCenterHeaders_(sheet);
    const properties = PropertiesService.getScriptProperties();
    if (!properties.getProperty('ALLOWED_ORIGINS'))
      properties.setProperty('ALLOWED_ORIGINS', 'https://hamghadamcare.ir,https://www.hamghadamcare.ir');
    if (!properties.getProperty('ALLOW_LOCAL_PREVIEW'))
      properties.setProperty('ALLOW_LOCAL_PREVIEW', 'false');
    return 'Ready: ' + CENTER_TAB;
  } finally { lock.releaseLock(); }
}

function doPost(event) {
  let data = {};
  let reply = { channel: 'hamghadam-center-v1', ok: false, persisted: false, code: 'SERVER_ERROR' };
  try {
    const raw = event && event.parameter && event.parameter.payload;
    if (typeof raw !== 'string' || raw.length > 20000) throw new Error('INVALID_REQUEST');
    data = JSON.parse(raw);
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('INVALID_REQUEST');
    if (!isUuid_(data.requestId) || !isUuid_(data.nonce)) throw new Error('INVALID_REQUEST');
    reply.requestId = data.requestId;
    reply.nonce = data.nonce;
    assertCenterOrigin_(data.origin);
    const values = validateCenterValues_(data);
    const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, JSON.stringify(values), Utilities.Charset.UTF_8);
    const hash = digest.map(value => (value & 255).toString(16).padStart(2, '0')).join('');
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(20000)) throw new Error('BUSY');
    try {
      const sheet = SpreadsheetApp.openById(CENTER_SPREADSHEET_ID).getSheetByName(CENTER_TAB);
      if (!sheet) throw new Error('SETUP_REQUIRED');
      assertCenterHeaders_(sheet);
      const lastRow = sheet.getLastRow();
      let row = null;
      if (lastRow > 1) {
        const match = sheet.getRange(2, 1, lastRow - 1, 1).createTextFinder(data.requestId)
          .matchEntireCell(true).useRegularExpression(false).findNext();
        if (match) row = match.getRow();
      }
      if (row !== null) {
        if (String(sheet.getRange(row, 8).getValue()) !== hash) throw new Error('ID_CONFLICT');
      } else {
        row = lastRow + 1;
        // Append exclusively. Other tabs and earlier rows are never rewritten.
        // Text format plus apostrophe escaping prevents spreadsheet formula execution.
        const range = sheet.getRange(row, 1, 1, CENTER_HEADERS.length);
        range.setNumberFormat('@');
        range.setValues([[
          data.requestId, new Date().toISOString(), 'در انتظار بررسی',
          literalCenterText_(values.name), literalCenterText_(values.phone),
          literalCenterText_(values.area), literalCenterText_(values.services), hash
        ]]);
        SpreadsheetApp.flush();
      }
      const saved = sheet.getRange(row, 1, 1, CENTER_HEADERS.length).getValues()[0];
      if (String(saved[0]) !== data.requestId || String(saved[7]) !== hash) throw new Error('VERIFY_FAILED');
      reply.ok = true;
      reply.persisted = true;
      delete reply.code;
    } finally { lock.releaseLock(); }
  } catch (error) {
    const codes = ['INVALID_REQUEST', 'INVALID_ORIGIN', 'VALIDATION_ERROR', 'BUSY', 'SETUP_REQUIRED', 'HEADER_MISMATCH', 'ID_CONFLICT', 'VERIFY_FAILED'];
    reply.code = codes.indexOf(error.message) >= 0 ? error.message : 'SERVER_ERROR';
    // Do not return exception details, sheet contents or contact data to the browser.
  }
  return centerReply_(reply, data && data.origin);
}

function assertCenterHeaders_(sheet) {
  const headers = sheet.getRange(1, 1, 1, CENTER_HEADERS.length).getValues()[0];
  if (headers.some((value, index) => value !== CENTER_HEADERS[index])) throw new Error('HEADER_MISMATCH');
}
function isUuid_(value) {
  return typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
}
function assertCenterOrigin_(origin) {
  const properties = PropertiesService.getScriptProperties();
  const origins = (properties.getProperty('ALLOWED_ORIGINS') || '').split(',').map(value => value.trim()).filter(Boolean);
  if (typeof origin !== 'string' || !(origins.indexOf(origin) >= 0 ||
      (origin === 'null' && properties.getProperty('ALLOW_LOCAL_PREVIEW') === 'true')))
    throw new Error('INVALID_ORIGIN');
}
function validateCenterValues_(data) {
  const limits = { name: 160, phone: 32, area: 200, services: 3000 };
  const values = {};
  Object.keys(limits).forEach(key => {
    if (typeof data[key] !== 'string' || data[key].length > limits[key]) throw new Error('VALIDATION_ERROR');
    values[key] = data[key].trim();
  });
  const normalized = values.phone.replace(/[۰-۹]/g, digit => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(digit)))
    .replace(/[٠-٩]/g, digit => String('٠١٢٣٤٥٦٧٨٩'.indexOf(digit))).replace(/[\s()\-]/g, '');
  if (!values.name || !values.area || !/^(?:0[1-9]\d{9}|(?:\+98|0098)[1-9]\d{9})$/.test(normalized))
    throw new Error('VALIDATION_ERROR');
  return values;
}
function literalCenterText_(value) { return value ? "'" + value : ''; }
function centerReply_(reply, origin) {
  // All replies contain only a nonce, ID and result. Never expose form data.
  const target = typeof origin === 'string' && /^https?:\/\/[^\s/]+$/.test(origin) ? origin : '*';
  const safeJson = value => JSON.stringify(value).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
  const html = '<!doctype html><meta charset="utf-8"><script>window.top.postMessage(' + safeJson(reply) + ',' + safeJson(target) + ');</script>';
  return HtmlService.createHtmlOutput(html).setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/** Run manually after setup. Appends ONE clearly labeled test row; never deletes it. */
function testCenterRequestRoundTrip() {
  const origin = (PropertiesService.getScriptProperties().getProperty('ALLOWED_ORIGINS') || '').split(',')[0].trim();
  const requestId = Utilities.getUuid();
  const sample = {
    requestId: requestId, nonce: Utilities.getUuid(), origin: origin,
    name: '[آزمایش اتصال] مرکز نمونه', phone: '۰۵۱۳۸۴۵۶۷۸۹',
    area: 'مشهد — داده آزمایشی', services: 'این ردیف فقط برای آزمایش اتصال و جلوگیری از ثبت تکراری است.'
  };
  for (let attempt = 0; attempt < 2; attempt++) {
    sample.nonce = Utilities.getUuid();
    const reply = doPost({ parameter: { payload: JSON.stringify(sample) } }).getContent();
    if (reply.indexOf('"persisted":true') < 0) throw new Error('Round-trip test failed: ' + reply);
  }
  const sheet = SpreadsheetApp.openById(CENTER_SPREADSHEET_ID).getSheetByName(CENTER_TAB);
  const matches = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).createTextFinder(requestId).matchEntireCell(true).findAll();
  if (matches.length !== 1) throw new Error('Duplicate detection failed');
  const row = sheet.getRange(matches[0].getRow(), 1, 1, CENTER_HEADERS.length).getValues()[0];
  if (!row[1] || row[2] !== 'در انتظار بررسی') throw new Error('Timestamp/status test failed');
  console.log('PASS: one saved test row, timestamp and pending status verified; retry produced no duplicate. Request ID: ' + requestId);
}
