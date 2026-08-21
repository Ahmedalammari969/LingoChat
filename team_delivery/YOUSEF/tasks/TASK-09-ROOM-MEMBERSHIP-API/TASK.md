# بناء مسار الانضمام ودالة التحقق من العضوية

## Task ID
`TASK-09-ROOM-MEMBERSHIP-API`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير مسار POST /api/v1/rooms/{room_id}/join ودالة is_user_member_of_room في backend/app/rooms/service.py للتحقق من العضوية ومعالجة حالتي 404 و 409.

## وصف المهمة
بناء وتطوير مسار POST /api/v1/rooms/{room_id}/join ودالة is_user_member_of_room في backend/app/rooms/service.py للتحقق من العضوية ومعالجة حالتي 404 و 409.

## لماذا هذه المهمة مهمة للنظام
تمكين المستخدمين من الانضمام للغرف وتوفير فحص أمني للعضوية يعتمد عليه الـ WebSocket.

## المتطلبات الوظيفية
- مسار الانضمام: التحقق من وجود الغرفة (404) وعدم العضوية المسبقة (409) وإضافة العضو وإرجاع 200.
- دالة is_user_member_of_room(db, room_id, user_id) -> bool سريعة وغير متزامنة.

## المتطلبات غير الوظيفية
- حماية من التكرار عبر القيود الفريدة.

## Edge Cases / الحالات الحدية
- انضمام مكرر -> 409 ALREADY_IN_ROOM.
- غرفة غير موجودة -> 404 ROOM_NOT_FOUND.

## الملفات المسموح بتعديلها
- `backend/app/rooms/schemas.py`
- `backend/app/rooms/service.py`
- `backend/app/rooms/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_rooms_membership.py`

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
- room_id و user_id.

## المخرجات المطلوبة
- سجل العضوية وحالة التحقق.

## نقاط التكامل مع أعضاء الفريق
- تستدعي دالة is_user_member_of_room مسارات الـ WebSocket ورسائل الغرف.

## Dependencies
- TASK-08-ROOMS-MANAGEMENT-API

## شروط اكتمال المهمة
- مسار انضمام ودالة عضوية معتمدة.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_rooms_membership.py -v

## طريقة التسليم
- تقرير فحص مسار الانضمام والعضوية.

## ممنوعات المهمة
- ممنوع السماح بانضمام مكرر لنفس المستخدم في الغرفة.
