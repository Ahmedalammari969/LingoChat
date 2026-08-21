# 04 - بناء عميل الـ API المركزي وإدارة JWT (04_API_CLIENT)

## الهدف
تطوير وتجهيز عميل الـ API المركزي في `frontend/src/api/client.js` لدعم استدعاءات HTTP وحقن رمز التوكن تلقائياً من `localStorage` ومعالجة الأخطاء المعيارية.

## اقرأ أولًا
- `team_package/contracts/API_CONTRACT.md`
- `team_package/contracts/SECURITY_CONTRACT.md`
- `frontend/src/api/client.js`

## الملفات المسموح تعديلها
- `frontend/src/api/client.js`
- `frontend/src/utils/constants.js` (إن وجد)

## الملفات الممنوع تعديلها
- `backend/**`
- `team_package/**`

## المتطلبات الوظيفية
1. ضبط عنوان الـ Base URL المعتمد: `http://localhost:8000/api/v1`.
2. حقن ترويسة `Authorization: Bearer <token>` تلقائياً عند توفر التوكن في `localStorage`.
3. ضبط ترويسة `Content-Type: application/json`.
4. معالجة استجابات الأخطاء القياسية (`error.code`, `error.message`).
5. التعامل التلقائي مع خطأ `401 Unauthorized` (مسح التوكن والتوجيه لتسجيل الدخول).

## المتطلبات غير الوظيفية
- عدم طباعة رمز الـ JWT في الـ console نهائياً.
- كود نظيف وقابل لإعادة الاستخدام في كافة خدمات الـ API.

## Edge Cases
- انقطاع الاتصال بالشبكة (Network Failure).
- استجابات الخادم غير المنسقة أو كود 500.

## خطوات التنفيذ
1. فتح وتحديث `frontend/src/api/client.js`.
2. كتابة دالة الإرسال المركزية (باستخدام fetch أو axios).
3. تطبيق دوال المساعدة لطلبات (GET, POST, PUT, DELETE).
4. تطبيق معالج الأخطاء المركزي (Centralized Error Handler).

## التحقق
- التأكد من إرسال الترويسات الصحيحة ومعالجة الأخطاء بمرونة.

## الاختبارات
- تنفيذ `05_API_CLIENT_TEST.md`.

## معايير النجاح
- توفير عميل API متكامل يلتزم بـ `API_CONTRACT.md` و `SECURITY_CONTRACT.md`.

## شروط التوقف
- التوقف عند حدوث أي خطأ في التعامل مع الـ Promises أو الترويسات.

## ممنوعات المهمة
- ممنوع طباعة التوكن في console.log.
- ممنوع تغيير مسار Base URL عن `/api/v1`.

## التسليم
- الانتقال للاختبار عبر `05_API_CLIENT_TEST.md`.
