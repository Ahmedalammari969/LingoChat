# 08 - معالجة وبث أحداث الانضمام والمغادرة (08_JOIN_LEAVE)

## الهدف
بناء وتطوير آلية بث حدث الانضمام `JOIN` فور قبول الاتصال، وبث حدث المغادرة `LEAVE` فور انقطاع أو إغلاق العميل للاتصال في `backend/app/websocket/router.py`.

## اقرأ أولًا
- `team_package/contracts/WEBSOCKET_CONTRACT.md` (هيكل أحداث JOIN و LEAVE)
- `backend/app/websocket/manager.py`

## الملفات المسموح تعديلها
- `backend/app/websocket/router.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `team_package/**`

## المتطلبات الوظيفية
1. **بث حدث `JOIN`**:
   - إرسال الرسالة لكافة أعضاء الغرفة فور قبول الاتصال:
     ```json
     {
       "type": "JOIN",
       "payload": {"user_id": "uuid", "username": "string"},
       "timestamp": "ISO8601 UTC",
       "room_id": "uuid"
     }
     ```
2. **بث حدث `LEAVE`**:
   - التقاط `WebSocketDisconnect` أو إغلاق القناة في كتلة `finally`.
   - استدعاء `manager.disconnect(room_id, user_id)`.
   - بث حدث `LEAVE` لبقية الأعضاء في الغرفة:
     ```json
     {
       "type": "LEAVE",
       "payload": {"user_id": "uuid", "username": "string"},
       "timestamp": "ISO8601 UTC",
       "room_id": "uuid"
     }
     ```

## المتطلبات غير الوظيفية
- ضمان بث حدث المغادرة حتى في حالات الانقطاع المفاجئ لشبكة العميل.

## Edge Cases
- انقطاع الاتصال قبل اكتمال التسجيل -> عدم بث أحداث مكررة أو خاطئة.

## خطوات التنفيذ
1. كتابة كود بث حدث `JOIN` بعد `manager.connect`.
2. وضع حلقة الاستقبال داخل `try...except WebSocketDisconnect...finally`.
3. كتابة كود بث حدث `LEAVE` في `finally`.

## التحقق
- مراقبة بث الأحداث عند دخول وخروج العملاء.

## الاختبارات
- تنفيذ `09_JOIN_LEAVE_TEST.md`.

## معايير النجاح
- بث أحداث الانضمام والمغادرة بالهيكل الرسمي الدقيق.

## شروط التوقف
- التوقف عند عدم إرسال حدث `LEAVE` بعد انقطاع الاتصال.

## ممنوعات المهمة
- ممنوع تعديل صيغة أو أسماء حقول أحداث JOIN و LEAVE.

## التسليم
- الانتقال للاختبار عبر `09_JOIN_LEAVE_TEST.md`.
