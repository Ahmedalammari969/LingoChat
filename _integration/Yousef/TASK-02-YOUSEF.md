# نموذج المستخدم وخدمات التشفير والأمان (User & Security Utilities)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-02-YOUSEF`
- **العضو المسؤول**: يوسف خيري
- **الدور**: مهندس قواعد البيانات والـ Backend
- **الحالة**: جاهزة للتنفيذ بعد TASK-01
- **الأولوية**: حرجة (Critical)

## 2. هدف المهمة

تنفيذ خدمات التشفير الآمن لكلمات المرور باستخدام `passlib[bcrypt]` (مع cost factor >= 12)، وإصدار والتحقق من رموز JWT باستخدام `python-jose[cryptography]` وفق خوارزمية `HS256`، وبناء الـ Schemas والـ Service الخاصة بالمستخدمين.

## 3. لماذا هذه المهمة؟

تأمين كلمات المرور وإدارة الجلسات عبر توكن JWT يمثل الطبقة الأمنية الأساسية لكامل النظام. تعتمد عليها واجهات REST API واتصالات الـ WebSocket للتحقق من هوية المستخدم وصلاحياته.

## 4. اقرأ هذه الملفات أولاً

- `docs/security.md` (الأقسام: 1 Secrets, 2 Password Hashing, 3 JWT)
- `docs/database-schema.md` (جدول `users`)
- `docs/api-contract.md` (التحقق من حقول المستخدم)
- `backend/app/core/config.py` (متغيرات `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)

## 5. الملفات المسموح تعديلها

- `backend/app/core/security.py`
- `backend/app/users/schemas.py`
- `backend/app/users/service.py`
- `backend/app/users/router.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_security.py`
- `backend/tests/unit/test_users.py`

## 8. المتطلبات الوظيفية

1. **دوال التشفير في `core/security.py`**:
   - `hash_password(plain_password: str) -> str`: تشفير كلمة المرور عبر bcrypt.
   - `verify_password(plain_password: str, hashed_password: str) -> bool`: التحقق من مطابقة كلمة المرور.
   - `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`: توليد توكن JWT مشفر مع تضمين `sub`, `exp`, `iat`.
   - `decode_access_token(token: str) -> dict`: فك تشفير والتحقق من توكن JWT وتوليد استثناء في حال الانتهاء أو التلاعب.
2. **مخططات Pydantic في `users/schemas.py`**:
   - `UserBase`: `username` (3-50 حرف، أحرف وأرقام وشرطة سفلية)، `preferred_language` (رمز ISO 639-1).
   - `UserCreate`: يرث من `UserBase` ويضيف `password` (8 أحرف على الأقل).
   - `UserResponse`: يرث من `UserBase` ويحتوي `id` (UUID) و `created_at`، ويمنع تماماً تضمين `hashed_password`.
3. **خدمة المستخدم في `users/service.py`**:
   - البحث عن مستخدم بواسطة `id` أو `username`.
   - إنشاء سجل مستخدم جديد وتخزين كلمة المرور مشفرة فقط.

## 9. المتطلبات غير الوظيفية

- **الأمان**: منع طباعة أو تسجيل (Log) كلمات المرور أو التوكنات.
- **صلاحية التوكن**: ضبط وقت انتهاء الصلاحية افتراضياً إلى 60 دقيقة (قابلة للتعديل عبر env).
- **منع تسريب البيانات**: التأكد بنسبة 100% أن `hashed_password` لا يعود في أي Response Model.

## 10. Edge Cases (الحالات الطرفية)

- كلمة مرور فارغة أو أقل من 8 أحرف (رفض عبر Pydantic Validation 422).
- اسم مستخدم يحتوي رموز غير مسموحة (فواصل، مسافات، رموز خاصة).
- توكن منتهي الصلاحية (Expired Token) -> إرجاع خطأ 401 Unauthorized.
- توكن تم التلاعب بتوقيعه (Tampered Signature) -> إرجاع خطأ 401 Unauthorized.
- توكن يحتوي تاريخ إصدار في المستقبل (`iat` in future) -> رفضه.

## 11. خطوات التنفيذ

- **الخطوة 1**: مراجعة دوال `backend/app/core/security.py` وتطبيق `CryptContext` مع `bcrypt`.
- **الخطوة 2**: كتابة دوال إنشاء وفك توكن JWT طبقاً لـ `docs/security.md`.
- **الخطوة 3**: كتابة مخططات `users/schemas.py` مع التحقق الصارم من المدخلات.
- **الخطوة 4**: تطبيق دوال البحث والإنشاء في `users/service.py`.
- **الخطوة 5**: إنشاء ملف اختبار `backend/tests/unit/test_security.py`.
- **الخطوة 6**: تشغيل الاختبارات والتأكد من النجاح.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-02-YOUSEF (نموذج المستخدم وخدمات التشفير والأمان).

قبل التنفيذ اقرأ الملفات التالية:
- docs/security.md
- docs/database-schema.md
- docs/api-contract.md
- backend/app/core/config.py

لا تنشئ مشروعًا جديدًا.
لا تغير Architecture.
لا تغير أسماء الـ Schemas أو دوال الأمان المعتمدة.
الملفات المسموح لك بتعديلها:
- backend/app/core/security.py
- backend/app/users/schemas.py
- backend/app/users/service.py
- backend/app/users/router.py
- وإنشاء: backend/tests/unit/test_security.py و backend/tests/unit/test_users.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. تطبيق تشفير bcrypt والتحقق منه في core/security.py.
2. تطبيق دوال create_access_token و decode_access_token لخوارزمية HS256 مع مطابقة معايير docs/security.md.
3. كتابة Pydantic Schemas في users/schemas.py للمستخدم (UserCreate, UserResponse, etc.) والتأكد من استبعاد hashed_password من الاستجابات.
4. كتابة خدمة المستخدمين users/service.py للتعامل مع قاعدة البيانات بشكل async.
5. كتابة اختبارات شاملة في backend/tests/unit/test_security.py لاختبار التشفير وصلاحية وانتهاء توكن JWT.

نفذ الخطوات وافحص الاختبارات وتأكد من خلو العمل من الأخطاء.
```

## 13. الاختبارات المطلوبة

- اختبار دالة `hash_password` والتحقق من عدم تساوي التشفير مع كلمة المرور الأصلية وتنوع الـ salt.
- اختبار دالة `verify_password` مع كلمات مرور صحيحة وخاطئة.
- اختبار إنشاء توكن JWT والتحقق من محتواه وصلاحيته.
- اختبار رفض التوكنات المنتهية أو المشوهة.
- تشغيل: `pytest backend/tests/unit/test_security.py`

## 14. شروط نجاح المهمة

- تشفير كلمات المرور باستخدام bcrypt بمستوى cost 12 على الأقل.
- استخراج والتحقق من JWT بكفاءة مع استجابة 401 في حال الخطأ.
- نجاح جميع اختبارات الأمان والمستخدمين 100%.

## 15. شروط عدم النجاح

- تخزين كلمة مرور دون تشفير.
- إمكانية ظهور `hashed_password` في `UserResponse`.
- قبول توكنات منتهية الصلاحية.

## 16. ممنوعات قطعية

- ممنوع استخدام خوارزمية تشفير ضعيفة أو تخزين مفتاح الـ JWT كنص ثابت.
- ممنوع طباعة التوكن أو كلمات المرور في Console/Logs.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Yousef/DELIVERY/DELIVERY-TASK-02.md`.
3. وثق نتائج اختبارات الأمان في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية أدوات التشفير وإصدار التوكنات لاستخدامها في مهام الـ Auth والـ WebSocket.
