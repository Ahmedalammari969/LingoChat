# بناء دالة اعتمادية المستخدم الحالي get_current_user

## Task ID
`TASK-07-USERS-AUTH-DEPENDENCY`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير دالة get_current_user كـ FastAPI Dependency لحماية المسارات والتحقق من ترويسة Authorization: Bearer <token>.

## وصف المهمة
بناء وتطوير دالة get_current_user كـ FastAPI Dependency لحماية المسارات والتحقق من ترويسة Authorization: Bearer <token>.

## لماذا هذه المهمة مهمة للنظام
تأمين مسارات النظام والتحقق من هوية المستخدم في كافة الطلبات المحمية.

## المتطلبات الوظيفية
- استخراج التوكن من ترويسة Authorization.
- فك التوكن واستخراج user_id وجلب المستخدم من قاعدة البيانات.
- إرجاع كائن User أو رفع خطأ 401 Unauthorized.

## المتطلبات غير الوظيفية
- سرعة تنفيذ وأمان كامل.

## Edge Cases / الحالات الحدية
- توكن مفقود أو منتهي أو مستخدم غير موجود -> 401.

## الملفات المسموح بتعديلها
- `backend/app/auth/service.py`
- `backend/app/auth/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_auth_dependency.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/SECURITY_CONTRACT.md`
- `_TEAM/00_SHARED/API_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `SECURITY_CONTRACT.md`
- `API_CONTRACT.md`

## المدخلات
- ترويسة الطلب HTTP.

## المخرجات المطلوبة
- كائن المستخدم الحالي الموثق.

## نقاط التكامل مع أعضاء الفريق
- حماية مسارات الغرف والرسائل ولوحة التحكم.

## Dependencies
- TASK-06-AUTH-LOGIN-JWT-API

## شروط اكتمال المهمة
- دالة اعتمادية أمنية معتمدة.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_auth_dependency.py -v

## طريقة التسليم
- تقرير فحص دالة الاعتمادية.

## ممنوعات المهمة
- ممنوع السماح بالوصول دون توكن صالح.
