# 12 - معالجة وبث مؤشر جاري الكتابة (12_TYPING)

## الهدف
بناء وتطوير معالج حدث `TYPING` الوارد من العميل في `backend/app/websocket/router.py` وبثه لجميع الأعضاء الآخرين في الغرفة مع استثناء المرسل.

## اقرأ أولًا
- `team_package/contracts/WEBSOCKET_CONTRACT.md` (هيكل حدث TYPING)

## الملفات المسموح تعديلها
- `backend/app/websocket/router.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `team_package/**`

## المتطلبات الوظيفية
1. استقبال حدث `TYPING` من العميل: `payload: {"is_typing": bool}`.
2. تجهيز حمولة البث للآخرين:
   ```json
   {
     "type": "TYPING",
     "payload": {
       "user_id": "uuid",
       "username": "string",
       "is_typing": true
     },
     "timestamp": "ISO8601 UTC",
     "room_id": "uuid"
   }
   ```
3. بث الرسالة لكافة أعضاء الغرفة مع استثناء المستخدم المرسل `exclude_user_id=user_id`.

## المتطلبات غير الوظيفية
- خفة وسرعة المعالجة الفائقة.

## Edge Cases
- إرسال حمولة `TYPING` بدون حقل `is_typing` -> إرجاع `ERROR` بكود `VALIDATION_ERROR`.

## خطوات التنفيذ
1. كتابة معالج نوع `TYPING` داخل حلقة الـ WebSocket.
2. استخراج حالة الكتابة وتجهيز الرسالة الصادرة.
3. استدعاء `manager.broadcast_to_room` مع تمرير `exclude_user_id`.

## التحقق
- مراقبة وصول حدث الكتابة للمستخدمين الآخرين وعدم ارتداده للمرسل.

## الاختبارات
- تنفيذ `13_TYPING_TEST.md`.

## معايير النجاح
- بث حدث الكتابة بالهيكل المعتمد بدقة.

## شروط التوقف
- التوقف عند حدوث أي خطأ في البث أو إرسال الحدث للمرسل نفسه.

## ممنوعات المهمة
- ممنوع تغيير اسم حقل `is_typing`.

## التسليم
- الانتقال للاختبار عبر `13_TYPING_TEST.md`.
