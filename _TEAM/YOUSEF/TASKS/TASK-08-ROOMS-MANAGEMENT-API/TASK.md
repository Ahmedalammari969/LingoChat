# بناء مسارات إنشاء واستعراض الغرف

## Task ID
`TASK-08-ROOMS-MANAGEMENT-API`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير مساري POST /api/v1/rooms و GET /api/v1/rooms في backend/app/rooms/router.py مع دعم الترقيم وحساب member_count وإضافة المنشئ كعضو تلقائياً.

## وصف المهمة
بناء وتطوير مساري POST /api/v1/rooms و GET /api/v1/rooms في backend/app/rooms/router.py مع دعم الترقيم وحساب member_count وإضافة المنشئ كعضو تلقائياً.

## لماذا هذه المهمة مهمة للنظام
إتاحة إنشاء غرف المحادثة واستعراضها للمستخدمين المسجلين.

## المتطلبات الوظيفية
- مسار POST /rooms: إنشاء الغرفة وإضافة المنشئ تلقائياً لـ room_members وإرجاع 201.
- مسار GET /rooms: استعراض الغرف مع limit و offset وحساب member_count وإرجاع 200.

## المتطلبات غير الوظيفية
- استعلامات تجميعية سريعة وتأمين المسارات بـ JWT.

## Edge Cases / الحالات الحدية
- اسم غرفة فارغ -> 422.
- ترقيم بقيم سالبة.

## الملفات المسموح بتعديلها
- `backend/app/rooms/schemas.py`
- `backend/app/rooms/service.py`
- `backend/app/rooms/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_rooms_api.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/API_CONTRACT.md`
- `_TEAM/00_SHARED/DATABASE_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `API_CONTRACT.md`
- `DATABASE_CONTRACT.md`

## المدخلات
- اسم الغرفة، معلمات الترقيم.

## المخرجات المطلوبة
- بيانات الغرف المنشأة والمسترجعة.

## نقاط التكامل مع أعضاء الفريق
- تستدعيها شاشة RoomsPage في الواجهة.

## Dependencies
- TASK-07-USERS-AUTH-DEPENDENCY

## شروط اكتمال المهمة
- مسارات غرف تطابق العقد 100%.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_rooms_api.py -v

## طريقة التسليم
- تقرير فحص مسارات الغرف.

## ممنوعات المهمة
- ممنوع نسيان إضافة منشئ الغرفة كعضو تلقائياً.
