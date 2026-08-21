# 02 - بناء بروتوكول ونماذج رسائل الويب سوكت (02_WEBSOCKET_PROTOCOL)

## الهدف
بناء وتطوير نماذج التحقق من صحة رسائل الويب سوكت في `backend/app/websocket/schemas.py` و `backend/app/websocket/protocol.py` للالتزام الصارم بغلاف الرسالة الموحد والأنواع الستة والحد الأقصى للحجم (4096 بايت).

## اقرأ أولًا
- `team_package/contracts/WEBSOCKET_CONTRACT.md`
- `backend/app/websocket/schemas.py`

## الملفات المسموح تعديلها
- `backend/app/websocket/schemas.py`
- `backend/app/websocket/protocol.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `team_package/**`

## المتطلبات الوظيفية
1. **نماذج Pydantic للرسائل والغلاف (Envelope)**:
   - `type`: Enum يحتوي حصراً: `["JOIN", "LEAVE", "TEXT_MESSAGE", "TYPING", "HEARTBEAT", "ERROR"]`.
   - `payload`: Dict مطابق للنوع المحدد.
   - `timestamp`: ISO8601 UTC.
   - `room_id`: UUID.
2. **دوال التحقق في `protocol.py`**:
   - التحقق من حجم النص الأقصى (<= 4096 بايت، وإلا رفع خطأ `MESSAGE_TOO_LONG`).
   - التحقق من سلامة الـ JSON (`INVALID_JSON`).
   - التحقق من نوع الرسالة (`UNKNOWN_MESSAGE_TYPE`).
   - دالة توليد رسائل الخطأ القياسية `create_error_message`.

## المتطلبات غير الوظيفية
- سرعة فحص فائقة وخفيفة على الذاكرة.

## Edge Cases
- إرسال نص مشوه ليس JSON -> `INVALID_JSON`.
- إرسال رسالة نصية فارغة -> `EMPTY_MESSAGE`.
- رسالة بحجم 5000 بايت -> `MESSAGE_TOO_LONG`.

## خطوات التنفيذ
1. تعريف Enum لأنواع الرسائل في `schemas.py`.
2. كتابة مخططات Pydantic للأنواع الستة.
3. كتابة دوال التحقق في `protocol.py`.

## التحقق
- تجربة التحقق من مختلف هياكل الرسائل والتأكد من مطابقتها.

## الاختبارات
- تنفيذ `03_WEBSOCKET_PROTOCOL_TEST.md`.

## معايير النجاح
- التزام كامل بنماذج `WEBSOCKET_CONTRACT.md`.

## شروط التوقف
- التوقف عند حدوث أي خطأ في التحقق من صحة النماذج.

## ممنوعات المهمة
- ممنوع إضافة حقول خارج الغلاف الموحد.

## التسليم
- الانتقال للاختبار عبر `03_WEBSOCKET_PROTOCOL_TEST.md`.
