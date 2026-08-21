# بناء مسار تسجيل مستخدم جديد

## Task ID
`TASK-05-AUTH-REGISTRATION-API`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير مسار POST /api/v1/auth/register في backend/app/auth/router.py للتحقق من البيانات وتشفير كلمة المرور وحفظ المستخدم وإرجاع 201 Created.

## وصف المهمة
بناء وتطوير مسار POST /api/v1/auth/register في backend/app/auth/router.py للتحقق من البيانات وتشفير كلمة المرور وحفظ المستخدم وإرجاع 201 Created.

## لماذا هذه المهمة مهمة للنظام
تمكين المستخدمين الجدد من إنشاء حساباتهم في LinguaChat.

## المتطلبات الوظيفية
- استقبال username, password, preferred_language.
- التحقق من عدم تكرار اسم المستخدم وإرجاع 409 USERNAME_ALREADY_EXISTS.
- تشفير كلمة المرور وحفظ المستخدم وإرجاع 201 Created دون كشف كلمة المرور.

## المتطلبات غير الوظيفية
- الالتزام بنموذج الأخطاء المعياري.

## Edge Cases / الحالات الحدية
- اسم مستخدم موجود مسبقاً (409).
- كلمة مرور أقل من 8 أحرف (422).

## الملفات المسموح بتعديلها
- `backend/app/auth/schemas.py`
- `backend/app/auth/service.py`
- `backend/app/auth/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_auth_register.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/API_CONTRACT.md`
- `_TEAM/00_SHARED/SECURITY_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `API_CONTRACT.md`
- `SECURITY_CONTRACT.md`

## المدخلات
- بيانات التسجيل.

## المخرجات المطلوبة
- حساب مستخدم جديد واستجابة 201.

## نقاط التكامل مع أعضاء الفريق
- تستدعيه شاشة التسجيل في الـ Frontend.

## Dependencies
- TASK-04-SECURITY-AND-PASSWORD-HASHING

## شروط اكتمال المهمة
- مسار تسجيل مستخدم متطابق 100% مع العقد.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_auth_register.py -v

## طريقة التسليم
- تقرير فحص مسار التسجيل.

## ممنوعات المهمة
- ممنوع إرجاع hashed_password في الاستجابة.
