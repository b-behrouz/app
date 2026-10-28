# انتشار خودکار روی میهن وب‌هاست — آماده، غیرفعال و بدون اتصال تأییدشده

دامنه: hamghadamcare.ir؛ URL نهایی مورد انتظار https://hamghadamcare.ir/ است. دامنه HTTP ارائه شده ولی canonical/OG موجود از قبل HTTPS است. SSL را فعال و صحت آن را تأیید کنید؛ HTTPS را صرفاً برای عبور تست غیرفعال نکنید. مرور دامنه از ابزار فعلی قابل انجام نبود؛ این به‌تنهایی خرابی سایت را ثابت نمی‌کند.

## آنچه آماده است

- `scripts/build_hosting.py`: خروجی اختصاصی ریشه دامنه، جدا از `/app/` گیت‌هاب؛ ۱۶ فایل، تقریباً ۹٫۳ MiB. HTML اصلی دقیقاً همان پیش‌نمایش است. مسیرهای مستقیم شناخته‌شده shell ریدایرکت به hash در ریشه دامنه دارند. 404.html برای مسیر ناموجود آماده است.
- `.github/workflows/deploy-hosting.yml`: بعد از موفقیت workflow «Verify local HTML» روی push شاخه main، همان commit را بررسی می‌کند. فقط زمانی منتشر می‌کند که HOSTING_ENABLED=true و زمان ساخت commit بعد از HOSTING_NOT_BEFORE باشد؛ re-run قدیمی نشر خودکار ندارد. اگر main جلو رفته باشد نسخه قدیمی منتشر نمی‌شود. فقط main مجاز است.
- ساخت و بررسی‌ها قبل از نوشتن روی هاست الزامی است. workflow دستی check فقط خواندنی است و هیچ فایلی روی هاست نمی‌نویسد. rollback دستی جداگانه و نیازمند تأیید ROLLBACK است.
- فقط index.html، 404.html، ورودی صفحات منتشرشده و یک manifest حاوی نام/هش/نسخه منتقل می‌شوند؛ سورس، node_modules، مستندات، آزمون‌ها، آرشیو مراکز، ایمیل یا تنظیمات هاست منتقل نمی‌شوند.
- FTPS صریح: AUTH TLS قبل از ارسال نام کاربری و رمز، گواهی و نام سرور بررسی می‌شود، PROT P و passive mode برای داده‌ها فعال است. fallback به FTP بدون TLS وجود ندارد. SSH/SFTP فرض نشده است؛ اگر سرویس فقط SFTP دارد ابتدا قابلیت دسترسی محدود و host key باید مشخص شود و این workflow برای آن روش بازنویسی شود.
- فایل‌های جدید در فایل‌های موقت اختصاصی آپلود و byte-by-byte readback می‌شوند؛ سپس rename انجام می‌شود. ابتدا فایل‌های کوچک و در پایان index و manifest تعویض می‌شوند. این تراکنش چندفایلی اتمیک کامل نیست. فایل‌های قدیمی نامرتبط یا مسیرهای خارج‌شده به صورت recursive حذف نمی‌شوند. shell قدیمی در صورت باقی‌ماندن به برنامه هدایت می‌کند و داده عمومی حذف‌شده را برنمی‌گرداند.
- برخورد با فایل ناشناس یا ویرایش دستی فایل مدیریت‌شده انتشار را قبل از نوشتن مسدود می‌کند. index.php موجود نیز توقف می‌دهد. فایل موجود تنها با هش دقیق manifest قبلی پذیرفته می‌شود. برای index.html اولیه، هش صریح مالک لازم است. .htaccess هرگز خوانده/بازنویسی نمی‌شود و تنظیمات ایمیل دست‌نخورده است.
- در خطای آپلود/rename بازگردانی فایل‌های تغییریافته همان اجرا تلاش می‌شود؛ شکست اتصال یا توقف کامل runner می‌تواند rollback را ناقص کند. در شکست بررسی عمومی یا UI، workflow ناموفق می‌شود و باید rollback دستی اجرا شود؛ بازگشت خودکار پس از خطای UI وعده داده نمی‌شود.

## اطلاعات غیرمحرمانه موردنیاز از cPanel

۱. Domains → hamghadamcare.ir → Document Root؛ مسیر واقعی را بفرستید، نه حدس public_html.
۲. Files → FTP Accounts → Configure FTP Client → Manual Settings: نام hostname دارای گواهی TLS معتبر، پورت، پشتیبانی Explicit FTP over TLS و passive mode. پورت ۲۱ رایج است ولی باید تأیید شود؛ FTPS implicit پورت ۹۹۰ با این پیاده‌سازی سازگار نیست.
۳. Security → SSL/TLS Status: اعتبار SSL برای hamghadamcare.ir و www در صورت استفاده. نسخه اصلی canonical بدون www است؛ انتقال www را مطابق تنظیمات موجود حفظ کنید.
۴. File Manager → Document Root: وجود index.php، index.html، .htaccess و قواعد مسیریابی فعلی را بررسی کنید. محتویات محرمانه را در چت نفرستید. اگر سایت دیگری در این پوشه است یا index.php دارد، خودکار آن را حذف نکنید؛ ابتدا مقصد اختصاصی برای هم‌قدم تعیین شود.
۵. Metrics/Files → Disk Usage: میزان فضای آزاد واقعی. با خروجی فعلی حدود ۲۰ MiB برای live+stage مصرف می‌شود؛ دست‌کم ۴۰ MiB آزاد پیشنهاد می‌شود تا خطا/فایل‌های موقت نیز جا داشته باشند. حجم کل هاست و ایمیل‌ها ممکن است همین سهمیه ۲۰۰ MB را مصرف کنند. build خروجی بیش از ۱۵ MiB را مسدود می‌کند؛ runtime آزادبودن quota را تضمین نمی‌کند. در قطع runner موقت‌های `.hamghadam-upload-*` با دقت و پس از بررسی اجراهای فعال پاک شوند؛ فایل‌های دیگر حذف نشوند.

## حساب محدود انتقال

cPanel → Files → FTP Accounts → Add FTP Account:
- نام پیشنهادی deploy-hamghadam؛ رمز قوی را فقط در password manager و GitHub Secret نگهداری کنید.
- Directory دقیقاً Document Root همین دامنه باشد. مسیر home حساب cPanel یا پوشه mail انتخاب نشود. اگر این Document Root شامل سایت‌های دیگر است، باید پوشه اختصاصی دامنه تعیین شود تا دسترسی به آنها نداشته باشد.
- محدودیت quota متناسب با فضای آزاد، مثلاً ۴۰ MB اگر سرویس اجازه دهد؛ quota حساب FTP جایگزین quota کل سرویس نیست.
- از حساب اصلی cPanel، root یا دسترسی SSH استفاده نکنید. از پشتیبانی بخواهید TLS برای command/data اجباری باشد.
- وقتی FTP account به Document Root محدود است، HOSTING_REMOTE_DIR معمولاً `/` است؛ مسیر سیستم `/home/user/public_html` لزوماً داخل chroot قابل مشاهده نیست. مسیر را با check تأیید کنید.

## Secrets و Variables گیت‌هاب

در https://github.com/b-behrouz/app → Settings → Environments یک environment به نام `production-hosting` بسازید؛ deployment branches فقط main. Secrets آن environment:

| Secret | مقدار |
| --- | --- |
| HOSTING_FTPS_HOST | hostname تأییدشدهٔ سرور، بدون scheme و بدون نام کاربری |
| HOSTING_FTPS_PORT | پورت Explicit FTPS تأییدشده |
| HOSTING_FTPS_USER | نام کاربری کاملِ حساب محدود ساخته‌شده |
| HOSTING_FTPS_PASSWORD | رمز همان حساب؛ فقط در Secret |
| HOSTING_REMOTE_DIR | مسیر داخل FTP، معمولاً / پس از محدودسازی حساب |
| HOSTING_INITIAL_INDEX_SHA256 | فقط اگر index.html اولیه وجود دارد: هش دقیقِ نمایش‌داده‌شده در check پس از تهیه نسخه پشتیبان و بررسی مالک؛ برای مقصد خالی نیازی نیست |

Settings → Secrets and variables → Actions → Variables (Repository variables):
- HOSTING_ENABLED در ابتدا `false`.
- HOSTING_NOT_BEFORE: زمان UTC فعال‌سازی با قالب `YYYY-MM-DDTHH:MM:SSZ`؛ برای مثال از ساعت فعلی خودتان پس از تنظیم استفاده کنید. این زمان را قبل از push بعدیِ تأییدشده ثبت کنید. commitهایی که قبل از این زمان ساخته شده‌اند منتشر نمی‌شوند.

رمزها را در YAML، فایل env مخزن، command line، چت یا log قرار ندهید. credentialهای انتقال فقط به step اتصال تزریق می‌شوند. حالت debug FTP فعال نشده است. هیچ Secret در این کار ساخته نشده است.

## اتصال اولیه بدون انتشار و ترتیب تأیید

۱. ابتدا HTML همین درخواست را بررسی و صریحاً اجازه push بدهید. تا آن زمان workflow فقط محلی است و روی GitHub وجود ندارد.
۲. پس از push مجاز، HOSTING_ENABLED همچنان false بماند. صرف اضافه‌کردن workflow یا Secret، انتشار انجام نمی‌دهد.
۳. Actions → Deploy production hosting → Run workflow → branch main → operation=check. این اجرا build و آزمون و TLS+login+encrypted passive data read را بررسی می‌کند؛ فایل یا folder روی هاست نمی‌نویسد. نتیجه check را بررسی کنید. این موفقیت به معنی امکان نوشتن یا نمایش سایت نیست.
۴. اگر مقصد index.html دارد، از cPanel قبل از اولین انتشار یک backup خارج از Document Root و ترجیحاً دانلود روی کامپیوتر خود تهیه کنید؛ فایل PHP/سایت نامرتبط را خودکار جایگزین نکنید. تنها پس از بررسی index اولیه، هش check را در Secret مربوط ثبت کنید. اولین محتوای قبلیِ نامرتبط در تاریخچه Git نیست و rollback آن با backup خودتان است.
۵. cPanel باید برای مسیر ناموجود 404.html را به‌عنوان ErrorDocument ارائه کند. بعد از بررسی .htaccess موجود، اگر ErrorDocument دیگری ندارد خط `ErrorDocument 404 /404.html` را به تنظیمات همان دامنه اضافه کنید؛ فایل موجود را جایگزین نکنید. مسیرهای مستقیم شناخته‌شده فایل واقعی دارند و بدون rewrite جدید کار می‌کنند. DirectoryIndex باید index.html را ارائه کند؛ اگر index.php مقدم است قبل از فعال‌سازی مقصد بررسی شود.
۶. بعد از check و پشتیبان‌گیری، HOSTING_NOT_BEFORE را به زمان فعلی UTC و HOSTING_ENABLED را true کنید. این تغییر به‌تنهایی deploy نمی‌کند. انتشار فقط بعد از push بعدی که HTML آن را بررسی و صریحاً تأیید کرده‌اید انجام می‌شود. برای اولین انتشار همین نسخه نیز بعد از تأیید شما یک commit انتشار جدید لازم است؛ rerun کامیت قدیمی ممنوع/مسدود است.
۷. SHA ریموت و workflow، HTTPS+hash عمومی و آزمون واقعی موبایل/دسکتاپ بررسی می‌شوند. فقط پس از آن اتصال موفق اعلام می‌شود. اجرای اول باید clean deep links، 404 و ارسال واقعی فرم را نیز تأیید کند؛ تست UI فرم عمداً داده واقعی نمی‌فرستد. ALLOWED_ORIGINS سرویس معرفی مرکز باید https://hamghadamcare.ir را شامل شود.

## بازگشت

SHA آخرین اجرای موفق production را از Actions نگه دارید. Actions → Deploy production hosting → Run workflow → main → operation=rollback → revision=SHA کامل همان نسخه → confirmation=ROLLBACK. کد deploy فعلی از تاریخچه همان SHA فقط HTML و داده لازم را می‌خواند؛ اسکریپت قدیمی را اجرا نمی‌کند. commit باید ancestor شاخه main باشد. قبل از rollback هم build/check اجرا می‌شود؛ خروجی قبلی بازسازی و منتشر و URL واقعی تست می‌شود. مسیرهای کوچک قدیمی حذف نمی‌شوند؛ اطلاعات عمومی از index انتخاب‌شده می‌آید. اگر crash قبلی manifest و فایل را نامنطبق کرد، برای جلوگیری از overwrite کور اجرای خودکار متوقف می‌شود؛ باید hash/فایل‌ها با backup یا مدیر هاست تطبیق داده شوند. تاریخچه و force push دستکاری نمی‌شوند. artifact ۱۴ روزه صرفاً کمک است و تنها راه rollback نیست.

## شبکه ایران و وضعیت واقعی

پشتیبانی همین پلن میهن وب‌هاست از FTPS، پورت passive، گواهی و دسترسی GitHub-hosted runner از خارج ایران هنوز تأیید نشده است. جست‌وجوی عمومی مدرک اختصاصی این حساب را مشخص نکرد. ایجاد account، دسترسی به cPanel یا SSH در این محیط موجود نیست؛ hostname و پورت هم هنوز ارائه نشده‌اند. امکان تست شبکه runner→هاست تا اجرای check وجود ندارد؛ از خطای ابزار مرور دامنه نمی‌توان محدودیت جغرافیایی را نتیجه گرفت.

از پشتیبانی بپرسید: «برای حساب من Explicit FTPS با TLS معتبر روی چه hostname/port و passive port range فعال است؟ آیا GitHub Actions runnerهای خارج ایران اجازه اتصال control و data دارند؟ آیا IP ثابت/allowlist، session reuse TLS یا محدودیت جغرافیایی اجباری است؟ آیا RNFR/RNTO با جایگزینی فایل در همان پوشه مجاز است؟»

اگر IP ثابت اجباری باشد، GitHub-hosted runner IP ثابت تضمین‌شده ندارد؛ راه‌حل runner اختصاصیِ مجاز و قابل‌دسترسی است که جداگانه پس از تأیید شما تنظیم می‌شود، نه حذف TLS یا FTP ساده. اگر quota یا فایروال مانع شود، اتصال موفق اعلام نمی‌شود و سایت موجود دست‌نخورده می‌ماند تا حدی که failure قبل از commit یا rollback موفق باشد.

منابع رسمی عمومی (تأیید محصول cPanel، نه همین حساب):
- https://docs.cpanel.net/cpanel/files/ftp-accounts/
- https://support.cpanel.net/hc/en-us/articles/4413517293719-Use-Web-Disk-or-FTPES-FTP-SSL-to-provide-secure-access-for-file-upload-management-without-sharing-cPanel-login-information

ساخت اولیه محتواییِ SSR/prerender ارائه نشده بود؛ همین ساختار موجود و metadata حفظ شده و prerender جدید ادعا نمی‌شود. og-image.png در منابع مستقل فعلی یافت نشد؛ فایل احتمالی موجود روی هاست حذف یا جایگزین نمی‌شود. در تست نهایی باید تصویر اشتراک‌گذاری و تنظیمات SEO موجود نیز بررسی شوند.


## آزمون اتصال مجاز در push تنظیمات

با تأیید صریح کاربر برای push و آزمون خواندنی، push تغییرات فایل workflow یا دو اسکریپت build_hosting/deploy_ftps روی main نیز فقط operation=check را اجرا می‌کند؛ این مسیر حتی با فعال‌بودن HOSTING_ENABLED حق نوشتن روی هاست ندارد. workflow_run همچنان تنها مسیر خودکار نشر پس از بررسی موفق و فعال‌سازی است. تغییر Secret یا Variable رویداد push نیست و اتصال یا نشر آغاز نمی‌کند.
