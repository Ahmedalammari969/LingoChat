# بروتوكول الويب سوكت ونماذج الرسائل والتحقق (WebSocket Protocol)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-01-MOHAMMED`
- **العضو المسؤول**: محمد الدعيـس
- **الدور**: مهندس الاتصال الفوري والويب سوكت
- **الحالة**: جاهزة للتنفيذ (Ready to Start)
- **الأولوية**: حرجة (Critical - Foundation)

## 2. هدف المهمة

بناء بروتوكول التحقق من صحة وبنية رسائل الويب سوكت في `backend/app/websocket/schemas.py` و `backend/app/websocket/protocol.py` للالتزام الصارم بغلاف الرسالة الموحد (Message Envelope) والأنواع الستة الرسمية (`JOIN`, `LEAVE`, `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`, `ERROR`) وتطبيق فحص الحجم الأقصى (4096 بايت).

## 3. لماذا هذه المهمة؟

الويب سوكت يتبادل رسائل غير متزامنة ذات تدفق ثنائي الاتجاه. إذا لم يكن هناك بروتوكول صارم يفحص صحة البيانات وسلامة الـ JSON وحجم الرسائل قبل معالجتها، سيتعرض النظام لانهيارات وأخطاء أمنية وفوضى في البيانات.

## 4. اقرأ هذه الملفات أولاً

- `docs/websocket-contract.md` (المصدر الأساسي للحقيقة لبروتوكول WebSocket وأنواع الرسائل)
- `docs/security.md` (القسم 6 الخاص بالتحقق من المدخلات)
- `docs/architecture.md` (القسم 3.3 و 7)

## 5. الملفات المسموح تعديلها

- `backend/app/websocket/schemas.py`
- `backend/app/websocket/protocol.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `backend/app/database/**` (خاص بيوسف خيري)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_websocket_protocol.py`

## 8. المتطلبات الوظيفية

1. **مخطط غلاف الرسالة الأساسي (Base Message Envelope)**:
   - `type`: نصي، ويجب أن يكون حتماً واحداً من: `["JOIN", "LEAVE", "TEXT_MESSAGE", "TYPING", "HEARTBEAT", "ERROR"]`.
   - `payload`: كائن (dict) يحتوي على تفاصيل الرسالة المحددة.
   - `timestamp`: نصي بصيغة ISO 8601 UTC.
   - `room_id`: نصي UUID.
2. **مخططات الـ Payloads للأنواع الستة**:
   - `JOIN`: `payload` يحتوي `{"user_id": UUID, "username": str}`.
   - `LEAVE`: `payload` يحتوي `{"user_id": UUID, "username": str}`.
   - `TEXT_MESSAGE (Outbound - Client->Server)`: `payload` يحتوي `{"text": str (1-4096 bytes), "original_language": str | None}`.
   - `TEXT_MESSAGE (Inbound - Server->Client)`: `payload` يحتوي `{"message_id": UUID, "sender_id": UUID, "sender_username": str, "original_text": str, "original_language": str, "translated_text": str, "target_language": str, "translation_source": str}`.
   - `TYPING (Client->Server)`: `payload` يحتوي `{"is_typing": bool}`.
   - `TYPING (Server->Clients)`: `payload` يحتوي `{"user_id": UUID, "username": str, "is_typing": bool}`.
   - `HEARTBEAT`: `payload` كائن فارغ `{}`.
   - `ERROR`: `payload` يحتوي `{"code": str, "message": str, "original_type": str | None}`.
3. **دوال الفحص والمعالجة في `protocol.py`**:
   - `parse_and_validate_message(raw_data: str) -> tuple[dict | None, dict | None]`:
     - فحص طول البيانات النصية (إذا تجاوز 4096 بايت -> إرجاع خطأ `MESSAGE_TOO_LONG`).
     - فك الـ JSON (إذا كان مشوهاً -> إرجاع خطأ `INVALID_JSON`).
     - التحقق من الـ Schema ونوع الرسالة (إذا كان النوع غير معروف -> إرجاع خطأ `UNKNOWN_MESSAGE_TYPE`).
     - إذا كان نص الرسالة فارغاً بعد تقليم المسافات -> إرجاع خطأ `EMPTY_MESSAGE`.
   - `create_error_message(code: str, message: str, room_id: str, original_type: str = None) -> dict`: توليد رسالة خطأ قياسية مطابقة للعقد.

## 9. المتطلبات غير الوظيفية

- **الأمان**: رفض أي رسالة غير مطابقة للـ schema قبل أن تستهلك موارد الخادم.
- **الأداء**: عمليات التحقق فائقة السرعة وخفيفة على الذاكرة.

## 10. Edge Cases (الحالات الطرفية)

- إرسال نص ليس بتنسيق JSON (مثل: `hello!`) -> كود `INVALID_JSON`.
- إرسال نوع غير معروف (مثل: `"type": "DELETE_CHAT"`) -> كود `UNKNOWN_MESSAGE_TYPE`.
- إرسال رسالة نصها مسافات فقط `"   "` -> كود `EMPTY_MESSAGE`.
- إرسال رسالة حجمها 5000 بايت -> كود `MESSAGE_TOO_LONG`.
- إرسال رسالة ينقصها حقل `room_id` أو `type` -> كود `VALIDATION_ERROR`.

## 11. خطوات التنفيذ

- **الخطوة 1**: مراجعة `backend/app/websocket/schemas.py` وكتابة نماذج Pydantic للأنواع الستة.
- **الخطوة 2**: كتابة دوال التحقق وتوليد الأخطاء في `backend/app/websocket/protocol.py`.
- **الخطوة 3**: كتابة اختبارات شاملة في `backend/tests/unit/test_websocket_protocol.py`.
- **الخطوة 4**: تشغيل الاختبارات والتأكد من نجاحها الكامل.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-01-MOHAMMED (بروتوكول الويب سوكت ونماذج الرسائل والتحقق).

قبل التنفيذ اقرأ الملفات التالية:
- docs/websocket-contract.md (المصدر المرجعي الأول)
- docs/security.md
- docs/architecture.md

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها:
- backend/app/websocket/schemas.py
- backend/app/websocket/protocol.py
- وإنشاء: backend/tests/unit/test_websocket_protocol.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. تعريف Enum لأنواع الرسائل الستة المعتمدة فقط: JOIN, LEAVE, TEXT_MESSAGE, TYPING, HEARTBEAT, ERROR.
2. بناء مخططات Pydantic الدقيقة لغلاف الرسالة وحمولات الأنواع الستة في websocket/schemas.py.
3. تطبيق دوال التحقق في websocket/protocol.py لمعالجة:
   - حجم الرسالة الأقصى 4096 بايت (MESSAGE_TOO_LONG)
   - سلامة الـ JSON (INVALID_JSON)
   - النص الفارغ (EMPTY_MESSAGE)
   - الأنواع غير المعروفة (UNKNOWN_MESSAGE_TYPE)
   - التحقق من الحقول (VALIDATION_ERROR)
4. كتابة اختبارات شاملة في backend/tests/unit/test_websocket_protocol.py.

نفذ الخطوات وافحص الاختبارات وتأكد من الجودة.
```

## 13. الاختبارات المطلوبة

- اختبار قبول كافة أنواع الرسائل الستة الصحيحة.
- اختبار رفض JSON غير صالح (INVALID_JSON).
- اختبار رفض نوع رسالة غير موجود (UNKNOWN_MESSAGE_TYPE).
- اختبار رفض الرسالة الفارغة (EMPTY_MESSAGE).
- اختبار رفض الرسائل أكبر من 4096 بايت (MESSAGE_TOO_LONG).
- تشغيل: `pytest backend/tests/unit/test_websocket_protocol.py`

## 14. شروط نجاح المهمة

- تطابق كامل مع `docs/websocket-contract.md`.
- تغطية كافة الحالات الطرفية ورموز الأخطاء.
- نجاح اختبارات البروتوكول 100%.

## 15. شروط عدم النجاح

- إضافة أنواع رسائل جديدة غير الأنواع الستة.
- قبول رسائل مشوهة أو تتجاوز 4096 بايت.

## 16. ممنوعات قطعية

- ممنوع تغيير هيكل الـ Envelope (type, payload, timestamp, room_id).
- ممنوع إرجاع كود خطأ غير موجود في جدول الأخطاء المعتمد.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Mohammed/DELIVERY/DELIVERY-TASK-01.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية بروتوكول ونماذج رسائل الـ WebSocket لبناء مدير الاتصالات والـ Router.
