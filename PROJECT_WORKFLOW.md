# مرجع الزام‌آور پروژهٔ هم‌قدم

آخرین بررسی: **۲۸ اکتبر ۲۰۲۶، منطقهٔ زمانی Asia/Tehran**.

commit مبنای بررسی: `081ca34056de8a659696c53f382409582c6b36e3`، روی شاخهٔ `main` محلی و GitHub. این سند و اصلاحات همراه آن هنوز commit/push نشده‌اند. هر وضعیت زمانی، شاهد همان بررسی است؛ قبل از عمل دوباره بررسی شود.

## ۱. هدف، تقدم قواعد و ترتیب قطعی

**اصلاح سورس → ساخت و تحویل HTML → بررسی و تأیید نسخهٔ HTML → آماده‌سازی گیت → تأیید مستقل push → push همان نسخه → آماده‌سازی هاست → تأیید مستقل انتشار با دامنه و SHA → انتشار فقط همان SHA → بررسی سایت واقعی.**

این مرجع بر دستورهای قدیمی پروژه برای انتشار خودکار هاست پس از push مقدم است. تأیید HTML مجوز push نیست؛ تأیید push مجوز انتشار روی هاست اصلی نیست. تأیید اتصال، ساخت Secret، سکوت کاربر، موفقیت CI یا دسترسی فنی هم مجوز انتشار نیستند. هر تأیید برای عملیات و نسخهٔ مشخص است؛ تغییر کد/خروجی پس از تأیید به بازبینی و تأیید نسخهٔ تازه نیاز دارد. یک بار تأیید چند مرحله فقط وقتی معتبر است که کاربر آن عملیات و نسخه‌ها را صریحاً نام برده باشد.

بدون دستور صریح: force push، reset مخرب، حذف تاریخچه، حذف فایل نامرتبط هاست یا تغییر تنظیمات حساب ممنوع است. هیچ رمز/توکن، محتوای Secret، اطلاعات خصوصی درخواست‌ها یا URL نشست cPanel در کد، سند، پیام یا log درج نشود. نام Secret و دامنهٔ عمومی محرمانه نیستند.

| مرحله | پیش‌نیاز | اقدام مجاز | خروجی | معیار اتمام | تأیید لازم |
| --- | --- | --- | --- | --- | --- |
| ۱: HTML محلی | درخواست تغییر و بررسی سورس/AGENTS/این سند | ویرایش سورس، ساخت و آزمون محلی، تحویل خود فایل | hamghadam-preview.html + گزارش آزمون/محدودیت | فایل واقعی قابل دریافت؛ تطبیق با سورس؛ بررسی رابط | تأیید نسخهٔ HTML؛ هیچ push مجاز نمی‌شود |
| ۲: گیت | همان نسخه و وضعیت تازهٔ گیت | بررسی remote/شاخه/تغییرات/مجوزها، آماده‌سازی فایل‌ها و diff؛ بدون push | خلاصهٔ دقیق تغییرات و شاخهٔ مقصد | نبود فایل نامرتبط یا محرمانه؛ خروجی تکرارپذیر | آماده‌سازی مجاز است؛ عبور به ۳ تأیید جدا می‌خواهد |
| ۳: push | تأیید صریح push برای نسخهٔ بررسی‌شده و شاخهٔ نام‌برده | stage مسیرهای صریح، commit، push عادی و تطبیق ریموت | شاخه، SHA کامل، نتیجه CI و اعلام وضعیت Pages | SHA ریموت برابر commit؛ شکست صریح گزارش شود | مستقل از تأیید HTML؛ مجوز هاست نیست |
| ۴: هاست | مقصد/روش انتقال معلوم و مجوز بررسی یا backup | بررسی فقط‌خواندنی اتصال و آماده‌سازی خروجی/backup؛ بدون نوشتن سایت | گزارش اتصال، خروجی ریشهٔ دامنه، پشتیبان بررسی‌شده | دامنه، مقصد، quota، backup و وضعیت مجوزها روشن | اتصال/backup فقط در محدودهٔ مجاز؛ نشر مجاز نیست |
| ۵: انتشار | SHA روی گیت، بررسی‌های موفق، backup و تأیید صریح همین عملیات | dispatch دستیِ deploy برای دامنه و SHA مصوب | انتقال، manifest و گزارش آزمون URL واقعی | محتوا و فلوها در موبایل/دسکتاپ و مسیرهای مستقیم تأیید شوند | تأیید مستقل «انتشار SHA … روی hamghadamcare.ir»؛ rollback نیز مستقل |

این درخواست فعلی فقط بررسی، آماده‌سازی و مستندسازی است؛ push، dispatch یا انتشار در آن مجاز نیست.

## ۲. نقشهٔ واقعی سورس و خروجی

ریشهٔ محیط فعلی `/workspace/app` است؛ در گفتگو/clone بعدی وجود این مسیر را فرض نکنید.

| مسیر | نقش واقعی |
| --- | --- |
| src/app.js | JavaScript بازیابی‌شده از HTML اولیه؛ بخش عمده minify و بخش‌های سفارشی خوانا؛ داده و تصاویر inline؛ پروژهٔ اولیه TSX/source map ارائه نشده |
| src/style-1.css | CSS اصلی و فونت‌های inline |
| src/style-2.css | فرم‌ها، هدر، نوار پایین و Alert مشترک |
| src/style-3.css | رنگ‌بندی Hero |
| src/index.template.html | پوسته، متادیتا و نشانگرهای جاسازی؛ div#root خالی ورودی اولیه |
| hamghadam-preview.html | خروجی واقعی و مستقل تک‌فایل؛ قابل استفاده با file:// و مسیریابی hash |
| index.html، 404.html، need/، feedback/، introduce-center/، centers/ | خروجی تولیدشده برای GitHub Pages؛ index دقیقاً برابر preview |
| config/pages.json | base_path فعلی /app/، فقط برای Pages |
| .pages-manifest.json، .nojekyll | فهرست خروجی مدیریت‌شده و جلوگیری از تولید صفحه از README |
| data/unpublished-centers.json | آرشیو ۷ مرکز با isPublished=false و listingStatus=unpublished؛ وارد HTML عمومی نمی‌شود |
| google-sheets/Code.gs و appsscript.json | کد معرفی مرکز و manifest سرویس Apps Script، نه سرویس منتشرشدهٔ قابل مشاهده از این محیط |
| google-sheets/configure.html | ابزار تنظیم آفلاین قبلی؛ اصل خروجی همیشه از src ساخته شود |
| scripts/ | ساخت، بررسی، کنترل push، FTPS و پشتیبان‌گیری؛ جزئیات زیر |
| tests/ | آزمون‌های VM، Python، مرورگر شبیه‌سازی‌شده، فایل محلی و URL زنده |
| work/، .private/ | محلی/موقت و gitignored؛ پشتیبان و خروجی آزمایش را وارد commit نکنید |
| docs/ | شواهد و راهنماهای تخصصی؛ وضعیت‌های تاریخی را با وضعیت جاری اشتباه نگیرید |

فهرست عمومی فعلی دقیقاً ۱۰ مرکز است؛ داده‌های ۷ مرکز خارج‌شده در docs/UNPUBLISHED-CENTERS.md تطبیق‌داده‌شده‌اند. جست‌وجو، فیلتر، شمارنده، پروفایل و JSON-LD از مجموعهٔ عمومی استفاده می‌کنند؛ صفحات خارج‌شده «مرکز پیدا نشد» دارند. build Pages ورودی آنها را تولید نمی‌کند.

### فرمان‌های ساخت و آزمون

در ریشهٔ مخزن اجرا شوند؛ نصب Node/Python برای توسعه است، نه برای بازکردن فایل تحویلی کاربر.

```bash
npm ci --ignore-scripts
python3 scripts/build_preview.py
python3 scripts/build_pages.py
python3 scripts/check_project.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_center_server.cjs
node tests/test_center_origin.cjs
node tests/test_public_centers.cjs
node tests/test_form_alerts.cjs
node tests/test_ui_refinements.cjs
node tests/test_pages.cjs
node tests/test_local_preview.cjs
```

Playwright در package-lock با نسخه 1.62.1 قفل است. مرورگر را از محیط معتبر انتخاب کنید؛ مثال این محیط:

```bash
CHROMIUM_PATH=/usr/bin/chromium node tests/test_local_preview.cjs
```

اجرای Chromium در این محیط ممکن است نیاز به مجوز اجرا داشته باشد و file:// با `ERR_BLOCKED_BY_ADMINISTRATOR` مسدود شده است. آن را دور نزنید و آزمون HTTP/mock را آزمون واقعی file معرفی نکنید. در runner GitHub، برای HTML فعلی با SHA256 زیر، آزمون واقعی file:// موبایل/دسکتاپ قبلاً موفق بوده؛ برای فایل تازه نتیجهٔ قبلی معتبر نیست.

SHA256 خروجی فعلی:
`7b92ea862d6917f0643e043e100385ddd3e8381ba4c57f21002c72dc8f562b69`

### قرارداد HTML و سرویس‌های آنلاین

خود فایل .html با فونت، CSS، JS، تصاویر و داده‌های لازم جاسازی‌شده تحویل شود؛ لینک سایت/localhost، کد پیام، مسیر داخلیِ غیرقابل‌دانلود یا ZIP جای آن نیست. پیش از تحویل بایت فایل دریافت‌شده را با خروجی مقایسه کنید. در این جلسه پیوست مستقیم ابزار نداشت؛ با تأیید قبلی کاربر فایل خصوصی Drive استفاده شده است:

- آخرین preview: https://drive.google.com/file/d/1N4V4BW7RXZHnZ6sMqD7ZxXIpQ_uOxtML/view
- نام دقیق: hamghadam-preview.html. قبل از replace متادیتا را بخوانید؛ بعد از upload فایل را readback و hash/cmp کنید. فایل را عمومی نکنید. این پیوند را با backup قدیمی هاست اشتباه نگیرید.

انتقال فرم به شیت به اینترنت/مجوز/نسخهٔ Apps Script وابسته است. معرفی مرکز از hidden POST iframe و پاسخ postMessage با channel، nonce، requestId و ok/persisted استفاده می‌کند؛ بدون تأیید واقعی موفقیت نشان ندهید. مبدأهای file/content/opaque به رشته null می‌روند و سرویس فقط با ALLOW_LOCAL_PREVIEW=true می‌پذیرد. origin payload احراز هویت نیست. کنترل اندازه، اعتبارسنجی، قفل، dedup و quota سادهٔ سرویس حفظ شود. endpoint معرفی مرکز اکنون همان URL عمومی پایان‌یافته به `AKfycbwPG9O4Ybynp97JAPGEgCVMRBNGli3HqQkYAZlln0NylYhlZFkfQgrtPZ8dgPD6jJcs9w/exec` در src است؛ اتصال بازخورد endpoint جدا دارد. وضعیت فعلی ثبت زندهٔ فرم‌ها و نسخهٔ واقعی Apps Script **تأییدنشده** است؛ تست mock/VM اثبات ذخیره زنده نیست.

## ۳. گیت، احراز هویت و workflowهای موجود

- مالک: `b-behrouz`؛ مخزن عمومی: https://github.com/b-behrouz/app
- origin: `https://github.com/b-behrouz/app.git`؛ انتقال HTTPS، SSH فرض نشده است.
- شاخهٔ فعلی و انتشار خروجی‌های ریشه: `main`. در بررسی API فقط main وجود داشت و `protected=false` بود. شاخه کاری دیگری مشاهده نشد؛ اگر شاخهٔ موقت لازم است با نام روشن بسازید، به‌عنوان وضعیت فعلی مستند جا نزنید.
- HEAD محلی و main ریموت در زمان بررسی همان commit مبنا بودند. working tree پیش از این درخواست تمیز بود.
- تنظیم branch.main.remote=origin و merge=refs/heads/main. fetch refspec محلی غیرمعمول `+HEAD:refs/remotes/origin/HEAD` است؛ origin/HEAD روی commit قدیمی e2894e6 دیده شد. بنابراین branch -avv به‌تنهایی وضعیت ریموت را ثابت نمی‌کند. بدون تغییر کور refspec، refs/heads/main را مستقیماً بررسی کنید.
- احراز هویت managed/proxy محیط، push HTTPS قبلی را ممکن کرده است؛ GitHub connector هم دسترسی read و rerun Actions موفق داشته. سازوکار داخلی/عمر token **تأییدنشده** است؛ credential helper صریح در config مشاهده نشد. نبود token قابل‌مشاهده به معنی نبود مجوز نیست. هیچ credential file یا env را dump نکنید.
- مجوز لازم برای push: contents write روی همین مخزن. برای dispatch/rerun: Actions write. workflowها خود `contents: read` دارند. مدیریت Environment/Secrets/Variables و branch protection دسترسی حساب می‌خواهد و از connector فعلی قابل تأیید کامل نیست. endpointهای secrets/admin ابزار محدودند؛ gh api قبلاً Forbidden داده و GitHub Actions دستور لازم را اجرا کرده است. token در چت درخواست نشود؛ از اتصال امن حساب استفاده شود.
- core.hooksPath=.githooks و hook pre-commit، scripts/check_project.py --staged را اجرا می‌کند. در clone تازه `python3 scripts/setup_git.py` اجرا شود.

### بررسی تازهٔ خواندنی

```bash
git status --short
git diff --stat
git diff --cached --stat
git remote -v
git branch -avv
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

آخرین فرمان نیاز به شبکه و مجوز دارد. در صورت نیاز، خواندن branch از GitHub connector جایگزین است. remote یا refspec شامل credential احتمالی را بی‌محابا در log چاپ نکنید. مقادیر کنونی این مخزن credential ندارند.

### نقش workflowها: remote مبنا در برابر اصلاح محلی این درخواست

| workflow | وضعیت روی GitHub در commit مبنا | نسخهٔ آمادهٔ محلی |
| --- | --- | --- |
| Verify local HTML / verify.yml | push، pull_request و dispatch؛ ساخت، کنترل اسرار، تست‌ها، مرورگر، artifact و بررسی زنده Pages | همان نقش؛ تست دروازهٔ مستقل انتشار نیز اضافه شده |
| Deploy production hosting / deploy-hosting.yml | push فایل‌های زیرساخت فقط check؛ workflow_run موفق CI می‌توانست با HOSTING_ENABLED=true منتشر کند؛ dispatch check/rollback هم داشت | **فقط workflow_dispatch** روی main؛ check/deploy/rollback، SHA کامل، SHA مصوب و عبارت تأیید شامل دامنه/عملیات/SHA؛ دیگر push/workflow_run ندارد |
| Back up current public index / backup-hosting.yml | push فایل‌های backup و dispatch؛ فقط دریافت index | در نسخهٔ آماده فقط dispatch؛ پشتیبان‌گیری خودکار ناشی از push هم حذف شده |
| pages build and deployment | workflow پویا/مدیریت‌شدهٔ GitHub Pages؛ main و ریشه، خارج از فایل‌های workflow پروژه؛ بعد از push اجرا می‌شود | در این درخواست تنظیم حساب تغییر نکرده؛ فقط مستند شده است |

نکتهٔ حساس: **اصلاح محلی، workflow فعال روی GitHub را عوض نکرده است.** تا تأیید مستقل push و ارسال این اصلاحات، نسخهٔ قدیمی روی ریموت باقی است. HOSTING_ENABLED در آخرین log بررسی‌شده false بود؛ مقدار زندهٔ امروز **تأییدنشده** است. قبل از هر push تازه از غیرفعال‌ماندن آن مطمئن شوید تا workflow قدیمی ناخواسته نشر نکند.

Pages در https://b-behrouz.github.io/app/ با push main ممکن است به‌روز شود؛ این با هاست اصلی متفاوت است. این اثر را در خلاصهٔ قبل از push به کاربر بگویید. تغییر تنظیمات Pages برای خاموش‌کردن انتشار فقط با دستور حساب مربوط انجام شود؛ این سند ادعای خاموش‌شدن Pages ندارد.

### commit و push مجاز

قبل از اقدام، فایل‌ها/خلاصه تغییرات، SHA یا hash خروجی بررسی‌شده و شاخهٔ مقصد را اعلام کنید؛ تأیید مستقل push بگیرید. سپس فقط مسیرهای همان درخواست را انتخاب کنید:

```bash
python3 scripts/finish_request.py --approved-push \
  --message 'Describe the approved request' \
  --paths PROJECT_WORKFLOW.md AGENTS.md
```

این مثال صرفاً برای دو مستند است؛ در کار واقعی تمام مسیرهای مربوط را صریحاً اضافه کنید. `.`، `git add -A` یا کل پوشهٔ نامرتبط انتخاب نشود. تغییرات زیرساخت همین درخواست نیز باید جدا در لیست اعلام‌شده بیایند. اسکریپت build/check، بررسی index stage، commit، push عادی و ls-remote برای تطبیق SHA را اجرا می‌کند؛ `--browser` بعضی تست‌های mock/Pages را اضافه می‌کند، نه همه تست‌ها. تست‌های مربوط به درخواست را پیش از آن جدا اجرا کنید. option --approved-push مجوز تولید نمی‌کند؛ فقط ثبت تأیید قبلاً دریافت‌شده است. اگر staged work قبلی وجود داشته باشد توقف می‌کند؛ آن را از بین نبرید.

در شکست push، commit محلی را نگه دارید و شکست را اعلام کنید. برای بازگشت گیت، پس از تأیید مناسب از `git revert <sha>` و commit عادی جدید استفاده شود؛ revert commit تغییر سایت هم نسخهٔ جدید است و به چرخهٔ HTML/push نیاز دارد. force push یا بازنویسی تاریخچه انجام نشود.

## ۴. نقشهٔ واقعی هاست و اتصال

| مورد | وضعیت/شاهد |
| --- | --- |
| سرویس | cPanel ایران، میهن وب‌هاست، ظرفیت ۲۰۰ MB؛ مطابق اعلام کاربر؛ ظرفیت آزاد فعلی **تأییدنشده** |
| دامنه | hamghadamcare.ir؛ کاربر HTTP داده، canonical و URL بررسی پروژه HTTPS است؛ اعتبار/نمایش HTTPS عمومی فعلی **تأییدنشده** |
| Document Root | public_html در home حساب cPanel، مطابق تصویر/اعلام کاربر؛ مسیر کامل خصوصی در این مرجع بازنشر نمی‌شود |
| حساب انتقال | FTP account محدود به همان public_html طبق تصویر کاربر؛ سطح محدودسازی تازهٔ حساب **تأییدنشده** |
| مسیر داخل FTPS | /، در ریشهٔ chroot حساب محدود؛ خواندن مقصد در آزمون موفق بوده |
| سرور گواهی | cp17.mihanvps.com؛ گواهی تصویر برای همین نام بود و TLS با آن موفق شد؛ ftp دامنه و IP با گواهی مطابقت نداشتند |
| پروتکل | Explicit FTPS روی پورت ۲۱، TLS معتبر و PROT P، passive؛ هیچ FTP ساده یا SSH استفاده نشد |
| شاهد اتصال | Actions run 40644032025، attempt 3، success؛ TLS+login+encrypted data+read موفق؛ نوشتن روی هاست انجام نشده |
| فایل موجود | index.html با حجم 104416 بایت؛ full tree و .htaccess، فایل‌های وابسته، quota و تنظیمات DirectoryIndex **تأییدنشده** |
| انتشار پروژه جدید | روی هاست اصلی انجام نشده؛ از موفقیت check/backup نمی‌توان write، rename، quota یا سلامت UI سایت اصلی را نتیجه گرفت |

شبکه GitHub-hosted runner → هاست ایران در آن آزمون خواندنی کار کرده است؛ این شاهد به معنی نبود محدودیت آینده، IP ثابت یا اجازه write نیست. دسترسی مستقیم shell محیط به دامنه قبلاً 403 بوده؛ علت دقیق ابزار/فایروال عمومی **تأییدنشده** است. TLS را برای رفع مشکل شبکه/گواهی خاموش نکنید.

### محل اتصال و Secretها

GitHub → repository Settings → Environments → `production-hosting` → Environment secrets:

| نام | کاربرد؛ مقدار محرمانه درج نشود |
| --- | --- |
| HOSTING_FTPS_HOST | hostname منطبق با گواهی TLS |
| HOSTING_FTPS_PORT | پورت FTPS صریح |
| HOSTING_FTPS_USER | نام کامل حساب محدود FTP |
| HOSTING_FTPS_PASSWORD | رمز همان حساب؛ فقط Secret |
| HOSTING_REMOTE_DIR | مقصد داخل chroot، با Document Root تطبیق داده شود |
| HOSTING_INITIAL_INDEX_SHA256 | برای پذیرش نخستین جایگزینی index موجود؛ فقط پس از backup و تأیید مستقل نشر مقدار هش درست ثبت شود |

در Settings → Secrets and variables → Actions → Variables، `HOSTING_ENABLED` یک کلید قطع/وصل فنی است و **تأیید انتشار نیست**؛ پیش‌فرض/آخرین شاهد false. `HOSTING_NOT_BEFORE` متعلق به workflow قدیمی است؛ در نسخهٔ آماده دیگر استفاده نمی‌شود و هیچ مجوزی ایجاد نمی‌کند.

نام پنج Secret در تصاویر کاربر درست بود؛ GitHub مقدار آنها را آشکار نمی‌کند. مسیر/نام Environment باید دوباره تطبیق داده شود. کاربر گزارش داد Deployment branches and tags را فقط main کرده؛ تنظیم فعلی از API محدود این محیط **تأییدنشده** است. Required reviewers برای Environment **تأییدنشده/فعال‌شده اعلام نشود**. اگر می‌خواهید GitHub هم تأیید انسانی را enforce کند، مالک باید در همین Environment reviewer مناسب را تنظیم کند؛ این دستیار دسترسی admin تأییدشده ندارد. دروازهٔ متنی SHA به‌تنهایی اثبات رضایت واقعی کاربر نیست؛ دستیار همچنان موظف به دریافت رضایت صریح است.

### خروجی هاست و سئو

```bash
python3 scripts/build_preview.py --check
python3 scripts/build_pages.py --check
python3 scripts/build_hosting.py --revision FULL_40_CHAR_SHA --output work/hosting-UNIQUE
HAMGHADAM_HOSTING_DIR=work/hosting-UNIQUE node tests/test_hosting_browser.cjs
```

SHA را فقط از commit تأییدشدهٔ موجود جایگزین کنید؛ خروجی باید پوشهٔ تازه/خالی باشد. builder محتوای hamghadam-preview.html و src/app.js همان revision را از git show می‌خواند؛ کد قدیمی را اجرا نمی‌کند. خروجی فعلی ۱۶ فایل و حدود ۹٫۳ MiB است: index.html، 404.html، سه shell فرم/نیاز، ده shell مرکز عمومی، `.hamghadam-deploy.json`. منابع اصلی inline هستند؛ build فایل توسعه/مدارک/node_modules/data archive را منتقل نمی‌کند. Pages همچنان /app/، هاست اصلی / است. HTML و متادیتا یکسان می‌مانند.

ورودی اولیه SSR/prerender محتوایی نداشت؛ فایل div#root را در مرورگر می‌سازد. حفظ این ساختار معادل ایجاد prerender جدید نیست. canonical/OG به https://hamghadamcare.ir/ اشاره می‌کنند؛ og-image.png در منابع مستقل موجود شناسایی نشد، وجود آن روی هاست **تأییدنشده** است و فایل احتمالی حذف نمی‌شود. .htaccess هرگز توسط اسکریپت نوشته نمی‌شود. برای 404 واقعی در cPanel باید تنظیم موجود بررسی و فقط با اجازهٔ مناسب `ErrorDocument 404 /404.html` به آن افزوده شود؛ تنظیمات قبلی را جایگزین نکنید. صفحات شناخته‌شده فایل واقعی دارند و به hash ریشه هدایت می‌شوند. full HTTP status و SEO مسیرها پس از انتشار باید آزمایش شوند.

### انتقال، ظرفیت و خطا

scripts/deploy_ftps.py از AUTH TLS پیش از ارسال credential، گواهی معتبر، TLS 1.2+ و کانال دادهٔ رمزنگاری‌شده استفاده می‌کند. `--check` فقط می‌خواند؛ بدون آن می‌نویسد و تا تأیید مرحلهٔ ۵ ممنوع است. نبود secret را با token چت جبران نکنید.

manifest و hash فایل مدیریت‌شده بررسی می‌شوند؛ وجود index.php یا برخورد با فایل ناشناس/ویرایش دستی توقف می‌دهد. index اولیه فقط با هش صریح پذیرش می‌شود. فایل جدید با نام موقت اختصاصی upload/readback شده و بعد rename می‌شود؛ index و manifest در آخر. حذف recursive یا mirror وجود ندارد؛ مسیرهای قدیمی ممکن است باقی بمانند ولی دادهٔ عمومی از index فعلی می‌آید. فایل/پوشهٔ نامرتبط، ایمیل و .htaccess حذف نمی‌شوند.

خروجی بیش از ۱۵ MiB مسدود است. برای حجم فعلی live+stage حدود ۲۰ MiB است؛ حداقل ۴۰ MiB فضای آزاد پیشنهاد می‌شود، نه تضمین. quota واقعی ۲۰۰ MB ممکن است با ایمیل/فایل‌های دیگر مشترک باشد؛ فضای آزاد و پشتیبان قدیمی را مالک از Disk Usage تأیید کند. روی هاست backup جدید ذخیره نمی‌شود. قطع کامل runner ممکن است temp برجای بگذارد؛ فقط temp مشخص همان اجرا و پس از اطمینان از عدم فعالیت بررسی/پاک شود، نه فایل دیگر.

بازگردانی فایل‌های تغییریافته در خطای upload/rename تلاش می‌شود؛ تراکنش چندفایلی اتمیک کامل نیست، قطع ارتباط می‌تواند rollback را ناقص کند. شکست بررسی عمومی/UI پس از transfer، rollback خودکار ندارد؛ workflow باید ناموفق گزارش و rollback مستقل آماده شود.

### پشتیبان واقعاً موجود

run موفق 40659075790، artifact 12802902376؛ فایل index از FTPS دو بار خوانده و بایت‌ها تطبیق داده شد. این **پشتیبان کامل هاست نیست**: فقط index.html و backup-manifest.json؛ بدون ایمیل، دیتابیس، .htaccess یا فایل جانبی.

- تاریخ UTC: 2026-10-28T08:45:39.994813+00:00
- حجم: 104416 بایت
- SHA256: `688b27b071e4855721303a7dec683e72b0d12f61db8a21689787bdb0c1d10dcb`
- نسخهٔ خصوصی تحویل‌شده: https://drive.google.com/file/d/1tQ3KSO_AW-TO309LrWPOBnqD3q_81kBW/view
- artifact گیت‌هاب ۷ روز نگهداری می‌شود؛ نسخه Drive را از artifact موقت تفکیک کنید. در گفتگوی بعد وجود و hash backup دوباره بررسی شود. backup قدیمی هاست را با preview جدید پروژه جایگزین نکنید.

برای backup تازه، فقط پس از مجوز مربوط، Actions → Back up current public index → Run workflow روی main. نسخهٔ محلی اصلاح‌شده فقط dispatch دارد. Download artifact با ابزار GitHub، اعتبارسنجی ZIP و hash، سپس تحویل امن فایل انجام شود. محتوی backup را داخل git یا log نریزید. backup زمان قبل را اثبات می‌کند؛ برای پذیرش اولیه بعد از تغییر سایت باید backup تازه و هش تازه بگیرید.

## ۵. انتشار با تأیید مستقل و بازگشت

قبل از اجرا دقیقاً اعلام کنید: «انتشار commit FULL_SHA روی https://hamghadamcare.ir/ در public_html». تأیید صریح همین عملیات را بگیرید؛ سپس Actions → Deploy production hosting → Run workflow روی main:

| input | مقدار برای نشر مجاز |
| --- | --- |
| operation | deploy |
| revision | SHA کامل ۴۰ کاراکتری هدف |
| approved_revision | دقیقاً همان SHA که کاربر برای هاست تأیید کرده |
| confirmation | DEPLOY hamghadamcare.ir FULL_SHA |

HOSTING_ENABLED باید true باشد، ولی تغییر آن به‌تنهایی نشر نمی‌کند. scripts/hosting_approval.py در نسخهٔ آماده فقط workflow_dispatch روی main را می‌پذیرد؛ event push/workflow_run، SHA متفاوت، نام شاخه به‌جای SHA، عملیات/دامنهٔ اشتباه و commit خارج از تاریخچهٔ main رد می‌شوند. ابزار اجرایی از github.sha اجرای workflow checkout می‌شود؛ payload دقیقاً از revision مصوب ساخته می‌شود، حتی اگر main بعداً جلو برود. اصلاحِ آماده تا پیش از push مجاز روی ریموت فعال نیست؛ روی workflow قدیمی dispatch نکنید.

در اجرای جدید ساخت/امنیت/تست‌های Python و VM روی نسخه ابزار اجرا می‌شوند، سپس bundle commit هدف ساخته و با مرورگر آفلاین قبل از upload بررسی می‌شود. بعد از upload، HTTPS و SHA فایل عمومی با bundle تطبیق داده می‌شود و tests/test_live_pages.cjs با HAMGHADAM_LIVE_URL و HAMGHADAM_LIVE_INDEX همان bundle روی موبایل/دسکتاپ اجرا می‌شود. این آزمون‌ها فرم واقعی ارسال نمی‌کنند. ورود/رفرش need، feedback، introduce-center، پروفایل، مسیر ناموجود، جست‌وجو/فیلتر، گالری، پشتیبانی، منابع، SSL و متادیتا جدا ارزیابی شوند. هر مسیر پوشش‌داده‌نشده اعلام شود؛ انتقال یا workflow سبز به‌تنهایی سلامت سایت را ثابت نمی‌کند.

برای بررسی دستی همان خروجی بدون ارسال فرم واقعی:

```bash
HAMGHADAM_LIVE_URL=https://hamghadamcare.ir/ \
HAMGHADAM_LIVE_INDEX=work/hosting-UNIQUE/index.html \
node tests/test_live_pages.cjs
```

rollback گیت با rollback هاست متفاوت است. برای برگشت هاست به یک commit قبلاً منتشرشده، دوباره دامنه/SHA را اعلام و تأیید مستقل بگیرید؛ dispatch با operation=rollback، revision و approved_revision برابر SHA هدف و confirmation برابر `ROLLBACK hamghadamcare.ir FULL_SHA`. همان مراحل build و آزمون واقعی اجرا می‌شود؛ force push ندارد. برای فایل قدیمی اولیهٔ هاست که commit پروژه نیست، backup index تنها مرجع همان فایل است؛ بازگردانی آن نیاز به اجازهٔ مشخص و انتقال محدودِ بررسی‌شده دارد و workflow فعلی restore از ZIP ندارد. اگر manifest با فایل‌های نیمه‌منتشرشده ناسازگار شد، اسکریپت برای جلوگیری از overwrite کور توقف می‌کند؛ رفع دستی با backup و اجازهٔ صاحب پروژه لازم است.

## ۶. وضعیت جاری، موارد تأییدنشده و ادامهٔ کار

تأییدشده در بررسی این درخواست: main ریموت همان مبنا، تنها شاخهٔ API main و محافظت‌نشده؛ اسکریپت‌ها/workflowهای فوق واقعاً در سورس موجودند؛ سابقهٔ check و backup از Actions API موفق خوانده شد. تغییر سایت/HTML در این درخواست لازم نیست و ظاهر تغییر نکرده است.

تأییدنشده و نباید موفق تلقی شود: مقدار فعلی Secret/Variables، جزئیات Environment/reviewer، فضای آزاد و tree کامل هاست، .htaccess/DirectoryIndex و SSL عمومی، مجوز نوشتن/rename، نشر واقعی نسخه جدید روی هاست، سلامت UI همان هاست، اتصال زنده فرم‌ها، نسخه جاری Apps Script. عدم قابلیت خواندن تنظیمات مدیریت حساب را از خرابی تنظیمات تفکیک کنید.

اقدام‌های حساب فقط وقتی دستیار واقعاً نمی‌تواند انجام دهد به مالک واگذار شوند: مشاهده/تغییر Secret در Environment، فعال‌سازی reviewer/main-only، تأیید Document Root و quota/.htaccess، رفع محدودیت host/IP با پشتیبانی. ابزارهای موجود برای read، backup، build، تست، commit/push و rerun را در محدودهٔ مجوز خود دستیار انجام دهد؛ رمز در چت نخواهد.

دستیار بعدی باید:

۱. این فایل و AGENTS.md را پیش از اقدام بخواند؛ درخواست جدید و مجوزهای معتبر همین نسخه را استخراج کند. این مستند به‌خودی‌خود هیچ مجوز push/nشر نمی‌دهد.
۲. وضعیت dirty/staged، remote، شاخه‌ها، SHA ریموت، workflow فعال و آخرین اجرای واقعی را دوباره بخواند؛ شواهد تاریخی را «امروز» معرفی نکند.
۳. تفاوت اصلاح محلی و ریموت را بررسی کند؛ مخصوصاً حذف محرک خودکار هاست. حتی اگر HOSTING_ENABLED=true باشد، رضایت مرحله ۵ ضروری است.
۴. خروجی را از سورس بسازد، hash فایل بررسی‌شده را نگه دارد و فقط همان نسخه را تحویل/ارسال/منتشر کند. هر خطای build/شبکه/مجوز یا آزمون انجام‌نشده را دقیق گزارش کند.
۵. قبل از push مستقل از HTML تأیید بگیرد؛ بعد از آن مستقل از push برای دامنه و SHA انتشار تأیید بگیرد. پس از هر اقدام وضعیت واقعی و SHA را گزارش کند.

در گفتگوهایی که فایل‌های پروژه خودکار خوانده نمی‌شوند، کاربر باید PROJECT_WORKFLOW.md و در صورت لزوم AGENTS.md را ضمیمه کند یا دستیار با دسترسی مجاز آنها را بخواند. ساخت این فایل حافظهٔ دائمی، اتصال حساب یا اتوماسیون فعال ایجاد نمی‌کند. اصلاحات این درخواست فقط در working tree آماده‌اند؛ تا درخواست صریح بعدی push یا انتشار انجام نشود.
