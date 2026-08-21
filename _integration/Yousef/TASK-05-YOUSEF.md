# حفظ الرسائل واسترجاع تاريخ المحادثات (Messages Persistence & History)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-05-YOUSEF`
- **العضو المسؤول**: يوسف خيري
- **الدور**: مهندس قواعد البيانات والـ Backend
- **الحالة**: جاهزة للتنفيذ بعد TASK-04
- **الأولوية**: عالية (High)

## 2. هدف المهمة

تنفيذ:
1. دوال حفظ الرسائل الأصلية والترجمات في قاعدة البيانات (`save_message`, `save_translation`).
2. مسار استرجاع تاريخ المحادثات الرسمي: `GET /api/v1/rooms/{room_id}/messages` مع الترقيم الزمني (Cursor/Time Pagination) والتحقق من عضوية المستخدم، وإرجاع النص الأصلي والنص المترجم للغة المستخدم المفضلة.

## 3. لماذا هذه المهمة؟

يحتاج المستخدم عند فتح غرفة المحادثة أو إعادة الاتصال إلى رؤية سجل الرسائل السابقة مترجمة بلغته المفضلة. كما تعتمد خدمة الـ WebSocket على خدمة الرسائل لحفظ المحادثات في الوقت الفعلي.

## 4. اقرأ هذه الملفات أولاً

- `docs/api-contract.md` (القسم 6 الخاص بـ `GET /rooms/{room_id}/messages`)
- `docs/database-schema.md` (جداول `messages` و `translations` و `room_members`)
- `docs/architecture.md` (القسم 3.4 وقواعد الـ Messages Service)

## 5. الملفات المسموح تعديلها

- `backend/app/messages/schemas.py`
- `backend/app/messages/service.py`
- `backend/app/rooms/router.py` (أو مسار رسائل الغرفة حسب الهيكلية)

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_messages.py`

## 8. المتطلبات الوظيفية

1. **دوال الخدمة في `messages/service.py`**:
   - `create_message(db, room_id, sender_id, text, language) -> Message`: حفظ رسالة جديدة في جدول `messages`.
   - `save_translation(db, message_id, target_lang, translated_text, provider, confidence) -> Translation`: حفظ أو تحديث ترجمة الرسالة في جدول `translations`.
   - `get_room_messages(db, room_id, user_lang, limit=50, before=None) -> tuple[list[dict], bool]`: جلب الرسائل السابقة مرتبة زمنياً، مع دمج الترجمة المتوافقة مع `user_lang` إن وجدت.
2. **مسار `GET /api/v1/rooms/{room_id}/messages`**:
   - حماية عبر Bearer JWT (معرف المستخدم ولغته المفضلة `preferred_language`).
   - التحقق من وجود الغرفة (إذا لم توجد: إرجاع `404 Not Found` كود `ROOM_NOT_FOUND`).
   - التحقق من عضوية المستخدم في الغرفة (إذا لم يكن عضواً: إرجاع `403 Forbidden` كود `FORBIDDEN`).
   - معلمات اختيارية: `limit` (افتراضي 50، أقصى حد 200)، `before` (توقيت ISO8601).
   - إرجاع استجابة `200 OK`:
     ```json
     {
       "messages": [
         {
           "id": "uuid",
           "room_id": "uuid",
           "sender_id": "uuid",
           "sender_username": "string",
           "original_text": "string",
           "original_language": "string",
           "translated_text": "string",
           "target_language": "string",
           "sent_at": "ISO8601"
         }
       ],
       "has_more": false
     }
     ```

## 9. المتطلبات غير الوظيفية

- **الأداء**: فهرسة `sent_at` واستخدام استعلامات `JOIN` محسنة لتجنب بطء استرجاع السجلات القديمة.
- **تطابق اللغات**: إذا كانت لغة الرسالة الأصلية مطابقة للغة المستخدم، يكون `translated_text = original_text` و `target_language = original_language`.

## 10. Edge Cases (الحالات الطرفية)

- مستخدم مسجل يحاول قراءة رسائل غرفة لم ينضم إليها -> 403 Forbidden (FORBIDDEN).
- طلب رسائل لغرفة فارغة تماماً -> إرجاع مصفوفة فارغة `messages: []` و `has_more: false`.
- تمرير معيار `before` غير صالح (Invalid Timestamp) -> معالجة وتجاهل أو إرجاع خطأ 422.
- رسالة لا تحتوي ترجمة محفوظة بعد للغة الهدف -> إرجاع `original_text` كقيمة احتياطية في `translated_text`.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص وتحديث مخططات الرسائل في `backend/app/messages/schemas.py`.
- **الخطوة 2**: كتابة دوال إنشاء وحفظ والبحث عن الرسائل والترجمات في `backend/app/messages/service.py`.
- **الخطوة 3**: ربط المسار `GET /rooms/{room_id}/messages` بالـ router وتطبيق فحوصات الأمان 403 و 404.
- **الخطوة 4**: كتابة اختبارات المسار والخدمة في `backend/tests/unit/test_messages.py`.
- **الخطوة 5**: تشغيل الاختبارات والتأكد من نجاحها بالكامل.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-05-YOUSEF (حفظ الرسائل واسترجاع تاريخ المحادثات).

قبل التنفيذ اقرأ الملفات التالية:
- docs/api-contract.md (القسم 6 الخاص بـ /rooms/{room_id}/messages)
- docs/database-schema.md (جداول messages و translations)
- docs/security.md (القسم 5 التحقق من عضوية الغرفة)

لا تنشئ مشروعًا جديدًا.
لا تغير أسماء الـ Endpoints أو حقول الاستجابات.
الملفات المسموح لك بتعديلها:
- backend/app/messages/schemas.py
- backend/app/messages/service.py
- backend/app/rooms/router.py
- وإنشاء: backend/tests/unit/test_messages.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. إعداد دوال create_message و save_translation في messages/service.py لحفظ البيانات في قاعدة البيانات.
2. تطبيق مسار GET /api/v1/rooms/{room_id}/messages مع التحقق الصارم من:
   - 401 عند غياب التوكن
   - 404 عند عدم وجود الغرفة
   - 403 عند عدم عضوية المستخدم في الغرفة
3. دعم الترقيم الزمني (limit و before) وإرجاع has_more.
4. إرجاع النص المترجم للغة المستخدم المفضلة مع النص الأصلي دائماً.
5. كتابة اختبارات شاملة في backend/tests/unit/test_messages.py.

نفذ الخطوات خطوة بخطوة وتأكد من نجاح الاختبارات.
```

## 13. الاختبارات المطلوبة

- اختبار حفظ واسترجاع الرسائل في قاعدة البيانات.
- اختبار استرجاع الرسائل بنجاح 200 لعضو في الغرفة.
- اختبار منع المستخدم غير المنضم بكود 403.
- اختبار الغرفة غير الموجودة بكود 404.
- اختبار التحقق من الترقيم و `has_more`.
- تشغيل: `pytest backend/tests/unit/test_messages.py`

## 14. شروط نجاح المهمة

- تطابق كامل لمسار تاريخ الرسائل مع `docs/api-contract.md`.
- عزل تام للمحادثات ومنع أي وصول غير مصرح لغير الأعضاء.
- نجاح كافة اختبارات الرسائل بنسبة 100%.

## 15. شروط عدم النجاح

- إرجاع رسائل الغرفة لمستخدم ليس عضواً فيها.
- عدم تضمين النص الأصلي `original_text` في الرد.
- فشل استعلامات الـ pagination.

## 16. ممنوعات قطعية

- ممنوع تعديل صيغة التاريخ والوقت عن ISO8601 UTC.
- ممنوع حذف الرسائل الأصلية عند الترجمة.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Yousef/DELIVERY/DELIVERY-TASK-05.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية مسار تاريخ الرسائل ودوال التخزين لربطها مع واجهات الدردشة في الـ Frontend ومعالجة الـ WebSocket.
