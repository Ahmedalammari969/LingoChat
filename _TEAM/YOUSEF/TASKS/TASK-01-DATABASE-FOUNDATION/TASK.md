# تهيئة قاعدة البيانات وجلسات الاتصال غير المتزامنة

## Task ID
`TASK-01-DATABASE-FOUNDATION`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
إعداد محرك SQLAlchemy Async وجلسات الاتصال ودالة get_db في backend/app/database/session.py.

## وصف المهمة
إعداد محرك SQLAlchemy Async وجلسات الاتصال ودالة get_db في backend/app/database/session.py.

## لماذا هذه المهمة مهمة للنظام
توفير البنية التحتية للتعامل مع قاعدة بيانات PostgreSQL بنمط غير متزامن عالي الكفاءة.

## المتطلبات الوظيفية
- تهيئة create_async_engine مع DATABASE_URL.
- تهيئة async_sessionmaker لإدارة الجلسات.
- دالة الاعتمادية get_db كـ FastAPI Dependency.

## المتطلبات غير الوظيفية
- إدارة الموارد وإغلاق الجلسات بأمان لمنع تسريب الاتصالات.

## Edge Cases / الحالات الحدية
- انقطاع الاتصال بقاعدة البيانات ومعالجة الأخطاء.

## الملفات المسموح بتعديلها
- `backend/app/database/session.py`
- `backend/app/database/base.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_database.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/DATABASE_CONTRACT.md`
- `backend/app/core/config.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `DATABASE_CONTRACT.md`

## المدخلات
- DATABASE_URL من التكوين.

## المخرجات المطلوبة
- محرك وجلسات قاعدة البيانات.

## نقاط التكامل مع أعضاء الفريق
- حقن get_db في كافة مسارات الـ API.

## Dependencies
- لا يوجد.

## شروط اكتمال المهمة
- اتصال قاعدة بيانات غير متزامن مستقر.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_database.py -v

## طريقة التسليم
- تقرير فحص تهيئة قاعدة البيانات.

## ممنوعات المهمة
- ممنوع استخدام دوال حظر متزامنة Blocking Calls مع قاعدة البيانات.
