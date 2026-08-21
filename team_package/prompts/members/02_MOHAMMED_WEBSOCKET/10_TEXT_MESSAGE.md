# 10 - معالجة الرسائل النصية وتوزيعها للمتلقين (10_TEXT_MESSAGE)

## الهدف
بناء وتطوير معالج الرسائل النصية `TEXT_MESSAGE` الواردة من العميل في `backend/app/websocket/router.py` والتحقق من صحتها وتوزيعها لكل عضو متصل في الغرفة بالهيكل الرسمي المحدد.

## اقرأ أولًا
- `team_package/contracts/WEBSOCKET_CONTRACT.md` (هيكل TEXT_MESSAGE للعميل والخادم)
- `team_package/docs/SYSTEM_STATES.md`

## الملفات المسموح تعديلها
- `backend/app/websocket/router.py`
- `backend/app/websocket/manager.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `team_package/**`

## المتطلبات الوظيفية
1. استقبال رسالة `TEXT_MESSAGE` من العميل:
   - فحص وجود `text` (1-4096 بايت).
   - استخراج `original_language` (أو `None`).
2. تجهيز هيكل الرسالة الصادرة لكل متلقٍّ:
   - `message_id`, `sender_id`, `sender_username`, `original_text`, `original_language`, `translated_text`, `target_language`, `translation_source`.
3. إرسال الرسالة إلى كافة المتواجدين في الغرفة.

## المتطلبات غير الوظيفية
- معالجة سريعة وتوزيع غير متزامن للرسائل.

## Edge Cases
- إرسال رسالة نصها فارغ أو مسافات فقط -> إرجاع `ERROR` بكود `EMPTY_MESSAGE` للمرسل فقط دون قطع الاتصال.
- رسالة أطول من 4096 بايت -> إرجاع `ERROR` بكود `MESSAGE_TOO_LONG`.

## خطوات التنفيذ
1. كتابة معالج نوع `TEXT_MESSAGE` داخل حلقة الـ WebSocket.
2. فحص محتوى النص وحجمه.
3. توزيع الرسالة عبر `manager.broadcast_to_room`.

## التحقق
- تجربة إرسال رسالة نصية واستلامها من طرف عميل آخر.

## الاختبارات
- تنفيذ `11_TEXT_MESSAGE_TEST.md`.

## معايير النجاح
- تسليم الرسائل النصية بالهيكل الرسمي لجميع المتواجدين في الغرفة.

## شروط التوقف
- التوقف عند حدوث أي خطأ يؤدي لقطع الاتصال عند استلام رسالة غير صالحة.

## ممنوعات المهمة
- ممنوع قطع الاتصال لمجرد إرسال رسالة خاطئة؛ بل يرسل إشعار `ERROR` فقط.

## التسليم
- الانتقال للاختبار عبر `11_TEXT_MESSAGE_TEST.md`.
