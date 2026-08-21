# بناء مسار إحصائيات لوحة التحكم

## Task ID
`TASK-11-DASHBOARD-STATS-API`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير مسار GET /api/v1/dashboard/stats في backend/app/dashboard/router.py لجلب التعداد التجميعي للمستخدمين والغرف والرسائل والترجمات والاتصالات النشطة.

## وصف المهمة
بناء وتطوير مسار GET /api/v1/dashboard/stats في backend/app/dashboard/router.py لجلب التعداد التجميعي للمستخدمين والغرف والرسائل والترجمات والاتصالات النشطة.

## لماذا هذه المهمة مهمة للنظام
توفير مؤشرات الأداء الحية وحجم استخدام النظام لشاشة Dashboard.

## المتطلبات الوظيفية
- استخراج total_users, total_rooms, total_messages, total_translations, active_connections.
- تأمين المسار برمز JWT وإرجاع 200 OK.

## المتطلبات غير الوظيفية
- استعلامات عد سريعة وخفيفة على قاعدة البيانات.

## Edge Cases / الحالات الحدية
- قاعدة بيانات فارغة -> إرجاع الأصفار بأمان.

## الملفات المسموح بتعديلها
- `backend/app/dashboard/service.py`
- `backend/app/dashboard/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_dashboard_api.py`

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

## المدخلات
- طلب GET مع JWT.

## المخرجات المطلوبة
- إحصائيات النظام الخمسة.

## نقاط التكامل مع أعضاء الفريق
- تستدعيها صفحة DashboardPage في الواجهة.

## Dependencies
- TASK-10-MESSAGE-PERSISTENCE-AND-HISTORY-API

## شروط اكتمال المهمة
- مسار إحصائيات دقيق ومتطابق مع العقد.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_dashboard_api.py -v

## طريقة التسليم
- تقرير فحص مسار الإحصائيات.

## ممنوعات المهمة
- ممنوع تغيير أسماء الحقول الإحصائية الخمسة.
