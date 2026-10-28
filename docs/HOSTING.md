# راهنمای هاست هم‌قدم — قاعدهٔ جاری

مرجع کامل و الزام‌آور: [PROJECT_WORKFLOW.md](../PROJECT_WORKFLOW.md)، به‌ویژه بخش‌های ۴ و ۵. این راهنما و AGENTS.md باید پیش از کار خوانده شوند.

از ۲۸ اکتبر ۲۰۲۶ دستور قدیمی «انتشار خودکار هاست بعد از push و CI موفق» لغو شده است. نسخهٔ آمادهٔ محلی workflow انتشار فقط workflow_dispatch دارد؛ deploy/rollback به تأیید مستقلِ عملیات، دامنه و SHA کامل نیاز دارد. HOSTING_ENABLED، موفقیت CI یا تأیید push جای آن نیستند. تا push مجاز اصلاحات، workflow قدیمی روی GitHub باقی است؛ تغییر محلی معادل تغییر سایت/حساب نیست.

خلاصه وضعیت تأییدشده در شواهد قبلی:

- دامنه hamghadamcare.ir، Document Root اعلامی public_html، حساب FTPS محدود به همان پوشه و مسیر داخل chroot برابر /.
- Explicit FTPS روی پورت ۲۱ با نام منطبق بر گواهی cp17.mihanvps.com؛ check شماره 40644032025، تلاش سوم، موفق بوده است.
- backup شماره 40659075790، فقط index.html واقعی با حجم 104416 بایت؛ full backup نیست. جزئیات hash و لینک امن در مرجع هستند.
- انتشار نسخه جدید روی هاست اصلی، امکان write/rename، SSL/UI عمومی، quota آزاد، تنظیمات .htaccess و مقدار جاری Secretها تأییدنشده‌اند.
- ساخت هاست: scripts/build_hosting.py با revision مشخص و خروجی در پوشه خالی؛ ریشه /، جدا از /app/ Pages.
- Secrets فقط در Environment production-hosting؛ در مرجع جدول نام‌ها، فرمان‌های ساخت، check، backup، کنترل quota و rollback آمده است. مقادیر رمز در هیچ سندی قرار نگیرند.

منابع رسمی برای امکانات عمومی cPanel (نه تأیید حساب فعلی):
- https://docs.cpanel.net/cpanel/files/ftp-accounts/
- https://support.cpanel.net/hc/en-us/articles/4413517293719-Use-Web-Disk-or-FTPES-FTP-SSL-to-provide-secure-access-for-file-upload-management-without-sharing-cPanel-login-information
