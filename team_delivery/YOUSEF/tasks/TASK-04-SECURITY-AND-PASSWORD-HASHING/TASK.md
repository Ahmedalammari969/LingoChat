# بناء دوال التشفير والأمان وإصدار JWT

## Task ID
`TASK-04-SECURITY-AND-PASSWORD-HASHING`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير دوال تشفير كلمات المرور باستخدام passlib[bcrypt] ودوال إنشاء وفك رموز JWT في backend/app/core/security.py.

## وصف المهمة
بناء وتطوير دوال تشفير كلمات المرور باستخدام passlib[bcrypt] ودوال إنشاء وفك رموز JWT في backend/app/core/security.py.

## لماذا هذه المهمة مهمة للنظام
توفير الأساس الأمني للتحقق من هوية المستخدمين وحماية كلمات المرور.

## المتطلبات الوظيفية
- دالة hash_password و verify_password بـ Bcrypt cost 12.
- دالة create_access_token مع خوارزمية HS256 وصلاحية 60 دقيقة وتضمين sub و username و preferred_language.
- دالة decode_access_token مع معالجة JWTError.

## المتطلبات غير الوظيفية
- الأمان الصارم وخلو الكود من الأسرار.

## Edge Cases / الحالات الحدية
- توكن منتهي الصلاحية أو توقيع مزور.

## الملفات المسموح بتعديلها
- `backend/app/core/security.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_security.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/SECURITY_CONTRACT.md`
- `backend/app/core/config.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `SECURITY_CONTRACT.md`

## المدخلات
- كلمات المرور والبيانات الحساسة.

## المخرجات المطلوبة
- دوال التشفير والـ JWT.

## نقاط التكامل مع أعضاء الفريق
- تستخدمها خدمات المصادقة ومسارات الـ WebSocket.

## Dependencies
- TASK-03-DATABASE-MIGRATIONS

## شروط اكتمال المهمة
- منظومة أمان وتشفير معتمدة 100%.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_security.py -v

## طريقة التسليم
- تقرير فحص دوال الأمان.

## ممنوعات المهمة
- ممنوع تقليل معامل كلفة Bcrypt عن 12.
