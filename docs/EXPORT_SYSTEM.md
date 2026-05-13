# نظام التصدير المتقدم (Export System)

## نظرة عامة
تم تصميم نظام التصدير في MyAtelier Pro لمعالجة مشاكل شائعة تتعلق بتسمية الملفات وحفظها عبر المتصفحات المختلفة، خاصة عند التعامل مع أسماء ملفات تحتوي على أحرف عربية أو رموز خاصة.

## المشكلة التاريخية (UUID Filenames Bug)
في الإصدارات السابقة، كان النظام يعتمد على توجيه المتصفح مباشرة إلى رابط التنزيل:
```javascript
// ❌ النهج الخاطئ القديم
window.location.href = download_url;
```
أو باستخدام وسم التحميل العادي:
```javascript
// ❌ النهج الخاطئ القديم
const link = document.createElement('a');
link.href = download_url;
link.download = '';
link.click();
```

**لماذا فشل هذا النهج؟**
عند استخدام هذه الطرق مع روابط تحتوي على معرّفات فريدة (UUID Tickets) مثل `/api/exports/download/12dbe1ba...`، يتجاهل المتصفح ترويسة `Content-Disposition` القادمة من الخادم ويقوم بتسمية الملف بالاعتماد على آخر جزء من الرابط (وهو الـ UUID). هذا يؤدي إلى تنزيل ملفات بأسماء عشوائية مثل `12dbe1ba-e21e-4503-8414-a4d5365ecedf` بدون امتداد.

## الحل المعماري المعتمد (Fetch + Blob)
لضمان احترام المتصفح لاسم الملف القادم من الخادم، نستخدم منهجية من 4 خطوات في دالة `downloadFile` الموجودة في `frontend/src/lib/api.ts`:

1. **إصدار التذكرة (Ticket Request):** طلب تذكرة تنزيل صالحة للاستخدام مرة واحدة من الخادم لضمان الأمان.
2. **جلب البيانات كـ Blob:** استخدام دالة `fetch()` لقراءة محتوى الملف برمجياً. هذا يسمح لنا بقراءة ترويسات الاستجابة (Headers).
3. **استخراج اسم الملف (Extract Filename):** قراءة ترويسة `Content-Disposition` واستخراج اسم الملف المرمّز بـ (RFC 5987) لدعم اللغة العربية.
4. **التحميل الإجباري (Blob URL Download):** تحويل الـ Blob إلى رابط محلي `URL.createObjectURL`، وإنشاء وسم `<a>` وتحديد خاصية `download` صراحة باسم الملف المستخرج.

```javascript
// ✅ النهج الصحيح المعتمد
const response = await fetch(ticketResult.download_url);
const disposition = response.headers.get('Content-Disposition') ?? '';
// ... استخراج filename ...
const blob = await response.blob();
const blobUrl = URL.createObjectURL(blob);
const link = document.createElement('a');
link.href = blobUrl;
link.download = filename; // إجبار المتصفح على استخدام هذا الاسم
link.click();
```

## تحذيرات هامة للمطورين (Protection Rules)
1. 🚫 **يُمنع منعاً باتاً** تغيير دالة `downloadFile` للعودة إلى استخدام `window.location.href` تحت أي ظرف.
2. ⚠️ في حالة وجود خطأ 500 أو 400 من الخادم، ستتراجع الدالة إلى `window.location.href = url` كحل أخير (Fallback). إذا رأيت ملفات يتم تنزيلها بأسماء عشوائية (UUID)، فهذا يعني أن الاستدعاء البرمجي لـ `fetch()` يفشل، وعليك مراجعة Logs الخاص بـ Backend (مثل مشكلة الصلاحيات أو اتصال قاعدة البيانات).
3. ♻️ **الكاش (Cache):** إذا استمرت مشكلة الأسماء العشوائية بعد تحديث الكود، فإن السبب بنسبة 99% هو احتفاظ المتصفح بنسخة قديمة (Cached JS Bundle). لحل المشكلة، قم بإغلاق المتصفح وفتحه، أو استخدام "Hard Refresh".
4. ⚙️ **إعدادات CORS:** الخادم مُعد لإرسال `Access-Control-Expose-Headers: Content-Disposition`. بدون هذا الإعداد، لن تتمكن دالة `fetch()` من قراءة اسم الملف، وسيعود النظام لتسمية الملف باسم افتراضي مثل `download.csv`.
