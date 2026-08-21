# بناء خدمة حفظ واسترجاع تاريخ الرسائل المترجمة

## Task ID
`TASK-10-MESSAGE-PERSISTENCE-AND-HISTORY-API`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير دوال create_message و save_translation ومسار GET /api/v1/rooms/{room_id}/messages مع الترقيم الزمني والتحقق من العضوية (403).

## وصف المهمة
بناء وتطوير دوال create_message و save_translation ومسار GET /api/v1/rooms/{room_id}/messages مع الترقيم الزمني والتحقق من العضوية (403).

## لماذا هذه المهمة مهمة للنظام
حفظ المحادثات في قاعدة البيانات وتمكين الأعضاء من قراءة الرسائل السابقة مترجمة بلغاتهم.

## المتطلبات الوظيفية
- دوال create_message و save_translation في messages/service.py.
- مسار GET /rooms/{id}/messages مع التحقق من عضوية المستخدم (403 FORBIDDEN) والغرفة (404).
- إرجاع الرسائل السابقة مع دمج النص المترجم للغة المستخدم.

## المتطلبات غير الوظيفية
- استعلامات JOIN محسنة وترقيم زمني قبل before.

## Edge Cases / الحالات الحدية
- مستخدم غير عضو يطلب الرسائل -> 403.
- غرفة فارغة -> مصفوفة فارغة messages: [].

## الملفات المسموح بتعديلها
- `backend/app/messages/schemas.py`
- `backend/app/messages/service.py`
- `backend/app/rooms/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_messages_api.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/API_CONTRACT.md`
- `_TEAM/00_SHARED/DATABASE_CONTRACT.md`
- `_TEAM/00_SHARED/SECURITY_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `API_CONTRACT.md`
- `DATABASE_CONTRACT.md`
- `SECURITY_CONTRACT.md`

## المدخلات
- room_id, limit, before.

## المخرجات المطلوبة
- سجل الرسائل المترجمة.

## نقاط التكامل مع أعضاء الفريق
- تستدعيها صفحة ChatPage وتستدعي دوال الحفظ مسارات WebSocket.

## Dependencies
- TASK-09-ROOM-MEMBERSHIP-API

## شروط اكتمال المهمة
- خدمة ومسار تاريخ رسائل متطابق 100% مع العقد.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_messages_api.py -v

## طريقة التسليم
- تقرير فحص مسار الرسائل والتخزين.

## ممنوعات المهمة
- ممنوع إرجاع الرسائل لمستخدم ليس عضواً في الغرفة.
