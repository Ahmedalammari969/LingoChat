# 06 - بناء واجهات المصادقة واختيار اللغة (06_AUTH_UI)

## الهدف
بناء وتطوير واجهات تسجيل الدخول والتسجيل واختيار اللغة المفضلة في `frontend/src/pages/LoginPage.jsx` مع ربطها بخطاف `useAuth.js` وخدمة المصادقة `api/auth.js`.

## اقرأ أولًا
- `team_package/contracts/API_CONTRACT.md` (مسارات /auth/register و /auth/login)
- `team_package/contracts/SECURITY_CONTRACT.md`
- `frontend/src/api/client.js`

## الملفات المسموح تعديلها
- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/hooks/useAuth.js`
- `frontend/src/api/auth.js`
- `frontend/src/services/auth.js`
- `frontend/src/components/**` (مكونات النماذج والأزرار)

## الملفات الممنوع تعديلها
- `backend/**`
- `team_package/**`

## المتطلبات الوظيفية
1. **نموذج تسجيل حساب جديد (Register)**:
   - استقبال: `username` (3-50 حرف)، `password` (8 أحرف فأكثر)، `preferred_language` (قائمة اللغات المدعومة).
   - استدعاء `POST /api/v1/auth/register`.
2. **نموذج تسجيل الدخول (Login)**:
   - استقبال: `username`, `password`.
   - استدعاء `POST /api/v1/auth/login`.
   - حفظ التوكن في `localStorage` وتحديث حالة `useAuth` والتوجيه لـ `/rooms`.
3. **خطاف المصادقة `useAuth.js`**:
   - إدارة حالة المستخدم وجلسة تسجيل الدخول ودالة `logout`.
4. **تجربة المستخدم**:
   - عرض مؤشر تحميل (Spinner) أثناء الإرسال.
   - عرض رسائل الخطأ بدقة وجاذبية (مثل 401 أو 409).

## المتطلبات غير الوظيفية
- عدم تخزين كلمة المرور في المتصفح.
- تصميم عصري زجاجي مع حركات ناعمة.

## Edge Cases
- اسم مستخدم مكرر (409) -> عرض تنبيه مخصص.
- كلمة مرور قصيرة -> تنبيه فوري قبل الإرسال.
- انقطاع الإنترنت -> تنبيه بفشل الشبكة.

## خطوات التنفيذ
1. كتابة دوال الاستدعاء في `frontend/src/api/auth.js`.
2. تجهيز خطاف `frontend/src/hooks/useAuth.js`.
3. بناء واجهة `frontend/src/pages/LoginPage.jsx`.
4. التحقق من المدخلات وربط الأحداث بالـ API.

## التحقق
- تجربة الانتقال بين شاشتي الدخول والتسجيل والتحقق من حفظ التوكن عند الدخول.

## الاختبارات
- تنفيذ `07_AUTH_UI_TEST.md`.

## معايير النجاح
- عمل تسجيل الدخول والتسجيل والتحقق من المدخلات بسلاسة تامة ومطابقة العقد.

## شروط التوقف
- التوقف عند حدوث أي خطأ في إدارة حالة الجلسة أو فقدان التوكن.

## ممنوعات المهمة
- ممنوع طباعة كلمة المرور أو التوكن في console.log.

## التسليم
- الانتقال للاختبار عبر `07_AUTH_UI_TEST.md`.
