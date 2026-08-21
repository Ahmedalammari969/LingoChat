# وحدة المصادقة والتسجيل وإصدار JWT (Auth Module)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-03-YOUSEF`
- **العضو المسؤول**: يوسف خيري
- **الدور**: مهندس قواعد البيانات والـ Backend
- **الحالة**: جاهزة للتنفيذ بعد TASK-02
- **الأولوية**: حرجة (Critical)

## 2. هدف المهمة

تنفيذ مسارات المصادقة الرسمية:
1. `POST /api/v1/auth/register` (تسجيل حساب جديد)
2. `POST /api/v1/auth/login` (تسجيل الدخول وإصدار رمز JWT)
مع التزام صارم بـ `docs/api-contract.md` ونموذج الأخطاء الموحد والـ Dependency الخاصة باستخراج المستخدم الحالي `get_current_user`.

## 3. لماذا هذه المهمة؟

تسجيل وحفظ المستخدمين والتحقق من هويتهم هو البوابة الأساسية لدخول النظام. وبدون هذا المسار، لن يتمكن الـ Frontend من تنفيذ عمليات التسجيل والدخول، ولن يتمكن باقي النظام من ربط العمليات بالمستخدمين.

## 4. اقرأ هذه الملفات أولاً

- `docs/api-contract.md` (القسم 1 و 2 الخاص بـ `/auth/register` و `/auth/login`)
- `docs/security.md` (القسم 3 و 6 و 10)
- `docs/database-schema.md` (جدول `users`)
- `backend/app/core/errors.py` (صيغة الأخطاء المعيارية)

## 5. الملفات المسموح تعديلها

- `backend/app/auth/schemas.py`
- `backend/app/auth/service.py`
- `backend/app/auth/router.py`
- `backend/app/main.py` (لتسجيل الـ router إذا لزم الأمر)

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_auth.py`

## 8. المتطلبات الوظيفية

1. **مسار `POST /api/v1/auth/register`**:
   - استقبال: `username` (3-50 حرف)، `password` (8 أحرف فأكثر)، `preferred_language` (رمز ISO 639-1).
   - التحقق من عدم تكرار اسم المستخدم (إذا وجد مسبقاً، إرجاع خطأ `409 Conflict` مع كود `USERNAME_ALREADY_EXISTS`).
   - تشفير كلمة المرور وحفظ المستخدم في قاعدة البيانات.
   - إرجاع استجابة `201 Created`:
     ```json
     {
       "id": "uuid",
       "username": "string",
       "preferred_language": "string",
       "created_at": "ISO8601"
     }
     ```
2. **مسار `POST /api/v1/auth/login`**:
   - استقبال: `username`, `password`.
   - التحقق من وجود المستخدم ومطابقة كلمة المرور المشفرة.
   - في حال عدم المطابقة: إرجاع خطأ `401 Unauthorized` مع كود `INVALID_CREDENTIALS` ورسالة عامة `"Invalid username or password"`.
   - إرجاع استجابة `200 OK`:
     ```json
     {
       "access_token": "string",
       "token_type": "bearer",
       "expires_in": 3600
     }
     ```
3. **الاعتمادية الأمنية `get_current_user`**:
   - التحقق من ترويسة `Authorization: Bearer <token>`.
   - استخراج المستخدم والتأكد من وجوده وتفعيله، أو إرجاع `401 Unauthorized`.

## 9. المتطلبات غير الوظيفية

- **الأمان**: عدم الكشف عما إذا كان الخطأ في اسم المستخدم أو كلمة المرور في شاشة الدخول لمنع User Enumeration.
- **تنسيق الأخطاء**: الالتزام التام بنموذج الأخطاء المعياري:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable description",
      "details": {}
    }
  }
  ```

## 10. Edge Cases (الحالات الطرفية)

- محاولة تسجيل اسم مستخدم موجود مسبقاً (إرجاع 409 USERNAME_ALREADY_EXISTS).
- إدخال كلمة مرور فارغة أو قصيرة (إرجاع 422 VALIDATION_ERROR).
- إدخال رمز لغة غير صالح (إرجاع 422).
- تسجيل دخول باسم غير موجود أو كلمة سر خاطئة (إرجاع 401 INVALID_CREDENTIALS).

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص وتحديث مخططات `backend/app/auth/schemas.py` لمطابقة الـ API Contract.
- **الخطوة 2**: كتابة منطق التسجيل والتحقق من الدخول في `backend/app/auth/service.py`.
- **الخطوة 3**: كتابة المسارات وتطبيق التبعيات في `backend/app/auth/router.py`.
- **الخطوة 4**: تطبيق دالة `get_current_user` كـ FastAPI Dependency.
- **الخطوة 5**: كتابة اختبارات المسارات في `backend/tests/unit/test_auth.py`.
- **الخطوة 6**: تشغيل الاختبارات والتأكد من تمريرها بالكامل.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-03-YOUSEF (وحدة المصادقة والتسجيل وإصدار JWT).

قبل التنفيذ اقرأ الملفات التالية:
- docs/api-contract.md (قسم Authentication و /auth/register و /auth/login)
- docs/security.md
- docs/database-schema.md
- backend/app/core/errors.py

لا تنشئ مشروعًا جديدًا.
لا تغير أسماء الـ Endpoints أو الـ Schemas.
الملفات المسموح لك بتعديلها:
- backend/app/auth/schemas.py
- backend/app/auth/service.py
- backend/app/auth/router.py
- backend/app/main.py
- وإنشاء: backend/tests/unit/test_auth.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. تطبيق مسار POST /api/v1/auth/register لإضافة مستخدم جديد مع إرجاع 201 وحساب التشفير.
2. تطبيق مسار POST /api/v1/auth/login للتحقق وإرجاع التوكن 200 OK.
3. معالجة كافة الأخطاء (400, 401, 409, 422) بالصيغة القياسية المحددة في docs/api-contract.md.
4. إعداد دالة get_current_user لحماية المسارات اللاحقة.
5. كتابة اختبارات شاملة في backend/tests/unit/test_auth.py والتأكد من نجاحها بالكامل.

نفذ الخطوات واختبر الكود بدقة.
```

## 13. الاختبارات المطلوبة

- اختبار تسجيل مستخدم جديد بنجاح وتلقي كود 201 مع استبعاد `hashed_password`.
- اختبار رفض تسجيل مستخدم مكرر بكود 409.
- اختبار تسجيل دخول ناجح واستلام `access_token`.
- اختبار رفض تسجيل الدخول ببيانات خاطئة بكود 401.
- تشغيل: `pytest backend/tests/unit/test_auth.py`

## 14. شروط نجاح المهمة

- تطابق كامل لمدخلات ومخرجات `/auth/register` و `/auth/login` مع `docs/api-contract.md`.
- عدم تسريب كلمات المرور المشفرة نهائياً في أي رد.
- نجاح كافة اختبارات الـ Auth بنسبة 100%.

## 15. شروط عدم النجاح

- تغيير مسار الـ endpoint عن `/api/v1/auth/*`.
- إرجاع صيغة أخطاء غير مطابقة للنموذج المعتمد.
- فشل أي اختبار مصادقة.

## 16. ممنوعات قطعية

- ممنوع إضافة حقول غير موجودة في العقد (مثل email أو phone).
- ممنوع تعديل صلاحيات المسارات المحمية دون JWT.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Yousef/DELIVERY/DELIVERY-TASK-03.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية مسارات التسجيل والدخول والـ JWT Dependency لبدء ربطها مع الـ Frontend ومسار الـ WebSocket.
