# اصلاح قرارداد مبدأ معرفی مرکز

سورس کامل سرویس: `google-sheets/Code.gs`؛ manifest کامل: `google-sheets/appsscript.json`.

## شواهد و محدودیت تشخیص

فایل پیوست کاربر فقط file: را صریحاً null می‌کند. در Android، content: ممکن است از ابتدا origin برابر null داشته باشد یا پیاده‌سازی دیگری ارائه کند. کد قبلی سرویس در مخزن null را فقط با ALLOW_LOCAL_PREVIEW دقیقاً true می‌پذیرد. تصویر INVALID_ORIGIN اثبات رد سیاست سرویس است، نه اثبات مقدار origin یا نسخه فعال. کد ارائه‌شده توسط کاربر با سورس قبلی مخزن تطبیق دارد؛ اما شماره نسخه فعال و مقادیر فعلی Properties ارائه نشده‌اند و تطبیق کد ادیتور با deployment هنوز قطعی نیست. پیام INVALID_ORIGIN جدید مبدأ ارسالی و build marker سرویس (یا قدیمی/نامشخص) را نمایش می‌دهد؛ هیچ فیلد فرم در تشخیص قرار نمی‌گیرد. اتصال مستقیم نیز به علت عدم دسترسی به proxy برقرار نشد؛ هیچ ثبت زنده‌ای تأیید نشده است.

## قرارداد جدید

file: و content: و origin رشته‌ای null به null نرمال می‌شوند؛ http/https مبدأ واقعی خود را می‌فرستند. سایر مبدأهای ناسازگار خطای صریح می‌گیرند. سرویس null را تنها با opt-in می‌پذیرد؛ سایر موارد باید دقیقاً http(s) origin در allowlist باشند. content:// خام و file:// و wildcard در فهرست مجاز قرار نگیرند. origin ادعایی قابل جعل است، احراز هویت نیست. وب‌اپ ورودی عمومی دارد؛ اعتبارسنجی، UUID/nonce، محدودیت اندازه، قفل، dedup پایدار، escape فرمول و readback ذخیره باقی مانده‌اند. سهمیه سراسری ۳۰ درخواست جدید در دقیقه زیر قفل اضافه شده است؛ retry ثبت‌شده سهمیه مصرف نمی‌کند. این کنترل ساده جایگزین CAPTCHA یا مقابله کامل با ربات نیست و IP در Apps Script قابل اتکا در دسترس نیست.

پاسخ به opaque origin نیاز به targetOrigin=* دارد؛ فقط نتیجه، شناسه، nonce و build marker ارسال می‌شود. پذیرش در کلاینت همچنان وابسته به origin معتبر Google + channel + nonce + requestId و ok/persisted است. اطلاعات تماس در پاسخ نیست. هیچ no-cors یا مبدأ آنلاین جعلی اضافه نشده است.

## انتشار توسط صاحب Apps Script

۱. Deploy → Manage deployments: Web app با URL فعلی ending /AKfycbwPG9O4Ybynp97JAPGEgCVMRBNGli3HqQkYAZlln0NylYhlZFkfQgrtPZ8dgPD6jJcs9w/exec را پیدا کنید. ابتدا کد Version فعال را با فایل تحویل‌شده تطبیق دهید. اگر پروژه شامل سرویس‌های دیگری است کدشان را حذف نکنید؛ قبل از جایگزینی Code.gs کد موجود را برای ادغام بفرستید.
۲. در پروژه اختصاصی معرفی مرکز، Code.gs و appsscript.json تحویل‌شده را جایگزین کنید. manifest از Project Settings → Show appsscript.json قابل نمایش است. scope جدید script.external_request فقط برای تست HTTP واقعی است.
۳. Project Settings → Script Properties: ALLOWED_ORIGINS شامل https://b-behrouz.github.io (بدون /app/ یا اسلش پایانی) باشد؛ دامنه‌های مجاز دیگر را حذف نکنید. ALLOW_LOCAL_PREVIEW برابر رشته true باشد. setupCenterRequests را اجرا کنید؛ مقدار موجود properties را خودکار تغییر نمی‌دهد و ردیف‌های موجود را بازنویسی نمی‌کند.
۴. diagnoseCenterTransport را اجرا کنید؛ خروجی version و دو تنظیم غیرمحرمانه را بررسی کنید. این خروجی نسخه ادیتور است.
۵. Deploy → Manage deployments → همان deployment → Edit (مداد) → Version: New version → Deploy. Execute as: Me؛ Who has access: Anyone. اگر حساب سازمانی این دسترسی را ممنوع کند نیاز به تنظیم مدیر دارد. با ویرایش همان deployment، URL فعلی حفظ می‌شود؛ New deployment لازم نیست. برای مجوز scope جدید فقط در صفحه رسمی گوگل تأیید کنید، هیچ رمز یا توکنی ارسال نکنید.
۶. URL فعلی /exec را باز کنید؛ JSON version باید 2026-10-27-local-origin-v2 باشد. اگر HTML قدیمی/خطا دیدید نسخه فعال هنوز تأیید نشده است.
۷. testDeployedCenterRequest را اجرا کنید. دو POST واقعی با شناسه یکسان و nonce متفاوت می‌فرستد و بعد از هرکدام شیت را برای دقیقاً یک ردیف، زمان و وضعیت در انتظار بررسی می‌خواند. ردیف با [آزمایش اتصال منتشرشده] مشخص است؛ حذف خودکار ندارد. فقط در صورت PASS نتیجه واقعی ثبت/dedup تأیید می‌شود. این تابع آزمون مرورگر و postMessage نیست؛ testCenterRequestRoundTrip صرفاً کد ادیتور را تست می‌کند.
۸. سپس HTML جدید را در file:// دسکتاپ، content:// اندروید و نسخه آنلاین آزمایش کنید. اکنون HTML جدید فقط محلی تحویل شده و سایت آنلاین به علت ممنوعیت push هنوز قدیمی است. هر محیطی که آزمایش نشده باید جدا گزارش شود.

## مرورگر اندروید

فایل را از تلگرام روی دستگاه دانلود کنید؛ در Files/Downloads گزینه Open with و Chrome یا مرورگر به‌روز پشتیبان HTML انتخاب کنید. وجود content:// به‌خودی‌خود خطا نیست؛ مسیر آن را به آدرس سایت آنلاین جعل نکنید. اگر مرورگر JavaScript، Web Crypto، POST در iframe یا postMessage را محدود کند حتی پذیرش null در سرویس کافی نیست. BROWSER_UNSUPPORTED پیش از ارسال و TIMEOUT فقدان تأیید پاسخ را نشان می‌دهد؛ TIMEOUT اثبات عدم ذخیره نیست و retry باید با همان اطلاعات/شناسه انجام شود. INVALID_ORIGIN مشخصاً رد سیاست سرویس است.

## وضعیت آزمون

تست‌های VM محلی و مرورگر با backend شبیه‌سازی‌شده انجام می‌شوند؛ معادل ثبت واقعی نیستند. مرورگر این محیط file:// را با ERR_BLOCKED_BY_ADMINISTRATOR مسدود می‌کند. دستگاه Android و نسخه فعال Apps Script در دسترس نیستند. ثبت واقعی، پاسخ iframe زنده و آزمون سه محیط هنوز تأیید نشده‌اند.
