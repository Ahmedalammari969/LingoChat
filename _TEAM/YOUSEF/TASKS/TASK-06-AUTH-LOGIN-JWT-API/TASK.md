# بناء مسار تسجيل الدخول وإصدار JWT

## Task ID
`TASK-06-AUTH-LOGIN-JWT-API`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير مسار POST /api/v1/auth/login في backend/app/auth/router.py للتحقق من بيانات الدخول وإصدار رمز access_token وإرجاع 200 OK.

## وصف المهمة
بناء وتطوير مسار POST /api/v1/auth/login في backend/app/auth/router.py للتحقق من بيانات الدخول وإصدار رمز access_token وإرجاع 200 OK.

## لماذا هذه المهمة مهمة للنظام
منح المستخدمين الموثقين رموز JWT للوصول إلى الغرف والرسائل والويب سوكت.

## المتطلبات الوظيفية
- استقبال username و password.
- التحقق من صحة البيانات وإرجاع 401 INVALID_CREDENTIALS عند الخطأ.
- توليد وإرجاع access_token مع expires_in=3600 واستجابة 200 OK.

## المتطلبات غير الوظيفية
- منع User Enumeration برسائل خطأ عامة.

## Edge Cases / الحالات الحدية
- اسم مستخدم غير موجود أو كلمة مرور خاطئة -> 401.

## الملفات المسموح بتعديلها
- `backend/app/auth/schemas.py`
- `backend/app/auth/service.py`
- `backend/app/auth/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_auth_login.py`

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
- بيانات الدخول.

## المخرجات المطلوبة
- access_token واستجابة 200 OK.

## نقاط التكامل مع أعضاء الفريق
- تستدعيه شاشة تسجيل الدخول في الواجهة.

## Dependencies
- TASK-05-AUTH-REGISTRATION-API

## شروط اكتمال المهمة
- مسار تسجيل دخول آمن وموثوق.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_auth_login.py -v

## طريقة التسليم
- تقرير فحص مسار الدخول.

## ممنوعات المهمة
- ممنوع كشف ما إذا كان اسم المستخدم هو الخاطئ أم كلمة المرور.
