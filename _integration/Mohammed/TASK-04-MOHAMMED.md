# معالجة الرسائل الحية والتوزيع والترجمة والانقطاع (Messaging & Translation)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-04-MOHAMMED`
- **العضو المسؤول**: محمد الدعيـس
- **الدور**: مهندس الاتصال الفوري والويب سوكت
- **الحالة**: جاهزة للتنفيذ بعد TASK-01 و TASK-02 و TASK-03
- **الأولوية**: حرجة جداً (Critical - Core Real-Time Engine)

## 2. هدف المهمة

تنفيذ حلقة معالجة الرسائل اللحظية (Event Loop) للاتصال المفتوح:
1. معالجة رسائل العميل الواردة: `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`.
2. استدعاء خدمة الترجمة `translate_message` لترجمة الرسالة النصية إلى اللغة المفضلة لكل متلقٍّ في الغرفة.
3. استدعاء خدمة الرسائل لحفظ الرسالة الأصلية والترجمات في قاعدة البيانات.
4. بث رسائل `TEXT_MESSAGE` المترجمة و `TYPING` لأعضاء الغرفة.
5. معالجة انقطاع الاتصال (Disconnect) وبث حدث `LEAVE` للمتبقين في الغرفة.

## 3. لماذا هذه المهمة؟

هذا هو القلب النابض لنظام LinguaChat؛ حيث تتلاقى خدمة الاتصال الحي مع خدمة الترجمة متعددة اللغات مع حفظ المحادثات في الوقت الفعلي.

## 4. اقرأ هذه الملفات أولاً

- `docs/websocket-contract.md` (القسم الخاص بـ `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`, `LEAVE`, `ERROR`)
- `docs/translation-contract.md` (استدعاء `translate_message` واستقبال الحقول `translated_text`, `source_used`)
- `docs/architecture.md` (القسم 5: Data Flow: Message Translation)
- `docs/security.md` (حماية الرسائل ومعالجة الأخطاء)

## 5. الملفات المسموح تعديلها

- `backend/app/websocket/router.py`
- `backend/app/websocket/manager.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/translation/**` (خاص بمؤيد الصوفي - تستدعي الواجهة فقط)
- `backend/app/database/models/**` (خاص بيوسف خيري)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/websocket/test_websocket_messages.py`
- `backend/tests/integration/test_websocket_translation.py`

## 8. المتطلبات الوظيفية

1. **حلقة الاستقبال والمعالجة (Message Receiving Loop)**:
   - استقبال الرسائل عبر `await websocket.receive_text()`.
   - فحص الرسالة عبر دالة البروتوكول `parse_and_validate_message(raw)`.
   - في حال وجود خطأ في البروتوكول: إرسال رسالة `ERROR` للعميل المرسل مع الإبقاء على الاتصال مفتوحاً.
2. **معالجة `HEARTBEAT`**:
   - تحديث توقيت الاتصال للعميل عبر `manager.record_heartbeat(room_id, user_id)` دون إرسال رد (Silent ACK).
3. **معالجة `TYPING`**:
   - بث حدث `TYPING` لجميع أعضاء الغرفة الآخرين مع تضمين `user_id`, `username`, `is_typing`.
4. **معالجة `TEXT_MESSAGE`**:
   - استخراج `text` و `original_language` (إذا كانت `None`، تمرر `"auto"` لخدمة الترجمة).
   - حفظ الرسالة الأصلية في قاعدة البيانات عبر استدعاء خدمة الرسائل `messages_service.create_message`.
   - **توزيع وترجمة الرسالة لكل متلقٍّ (Per-Recipient Translation)**:
     - لكل مستخدم متصل في الغرفة:
       - معرفة لغته المفضلة `target_lang = recipient.preferred_language`.
       - استدعاء خدمة الترجمة:
         ```python
         try:
             res = await translate_message(text, source_lang=source_lang, target_lang=target_lang)
             translated_text = res["translated_text"]
             translation_source = res["source_used"]
         except TranslationError:
             translated_text = text  # Fallback to original
             translation_source = "libretranslate"
             # إرسال رسالة خطأ تحذيرية للمرسل أو المستلم
         ```
       - حفظ الترجمة الجديدة في قاعدة البيانات عبر `save_translation`.
       - إرسال الرسالة إلى المتلقي بالهيكل الرسمي المحدد في `docs/websocket-contract.md`:
         ```json
         {
           "type": "TEXT_MESSAGE",
           "payload": {
             "message_id": "uuid",
             "sender_id": "uuid",
             "sender_username": "string",
             "original_text": "string",
             "original_language": "string",
             "translated_text": "string",
             "target_language": "string",
             "translation_source": "libretranslate | google | cache | identity"
           },
           "timestamp": "ISO8601",
           "room_id": "uuid"
         }
         ```
5. **معالجة الانقطاع (Disconnect / LEAVE Event)**:
   - عند إغلاق العميل للاتصال أو حدوث استثناء `WebSocketDisconnect`:
     - استدعاء `manager.disconnect(room_id, user_id)`.
     - بث حدث `LEAVE` لكافة الأعضاء المتبقين في الغرفة:
       ```json
       {
         "type": "LEAVE",
         "payload": {
           "user_id": "uuid",
           "username": "string"
         },
         "timestamp": "ISO8601",
         "room_id": "uuid"
       }
       ```

## 9. المتطلبات غير الوظيفية

- **التكامل المعماري**: عدم استدعاء مزودي الترجمة مباشرة، بل استدعاء `translate_message` من `translation/service.py` حصراً.
- **التوافقية العالية**: معالجة الترجمات المتعددة بالتوازي (باستخدام `asyncio.gather`) لضمان سرعة التسليم في الغرف الكبيرة.

## 10. Edge Cases (الحالات الطرفية)

- المرسل والمستقبل يملكان نفس اللغة -> التأكد من أن `translation_source == "identity"` و `translated_text == original_text`.
- فشل جميع مزودي الترجمة -> تسليم الرسالة بالنص الأصلي وإرسال إشعار `ERROR` دون قطع الاتصال.
- قطع أحد العملاء للاتصال أثناء قيام الخادم بالبث -> عدم تأثر بقية المتلقين.
- إرسال رسالة فارغة -> إرسال `ERROR` بكود `EMPTY_MESSAGE` للمرسل فقط.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص مسار `backend/app/websocket/router.py`.
- **الخطوة 2**: ربط استدعاء `translate_message` و `messages_service` داخل حلقة معالجة الرسائل.
- **الخطوة 3**: كتابة بث حدث `LEAVE` في كتلة `finally` أو عند التقاط `WebSocketDisconnect`.
- **الخطوة 4**: كتابة اختبارات شاملة في `backend/tests/websocket/test_websocket_messages.py` و `backend/tests/integration/test_websocket_translation.py`.
- **الخطوة 5**: تشغيل كافة اختبارات الويب سوكت والتكامل والتأكد من نجاحها 100%.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-04-MOHAMMED (معالجة الرسائل الحية والتوزيع والترجمة والانقطاع).

قبل التنفيذ اقرأ الملفات التالية:
- docs/websocket-contract.md (الأقسام الخاصة بـ TEXT_MESSAGE, TYPING, HEARTBEAT, LEAVE, ERROR)
- docs/translation-contract.md
- docs/architecture.md (Data Flow)

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها:
- backend/app/websocket/router.py
- backend/app/websocket/manager.py
- وإنشاء: backend/tests/websocket/test_websocket_messages.py و backend/tests/integration/test_websocket_translation.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. معالجة رسائل TEXT_MESSAGE و TYPING و HEARTBEAT الواردة من العميل.
2. استدعاء دالة translate_message من translation/service.py لترجمة الرسالة إلى اللغة المفضلة لكل متلقٍّ في الغرفة.
3. استدعاء messages/service.py لحفظ الرسالة الأصلية والترجمات.
4. إرسال TEXT_MESSAGE لكل مستخدم بالهيكل الرسمي المحدد في websocket-contract.md مع تضمين original_text و translated_text و translation_source.
5. إرسال حدث LEAVE للمتبقين عند انقطاع أي مستخدم.
6. كتابة اختبارات تكاملية شاملة للويب سوكت والترجمة في backend/tests/websocket/test_websocket_messages.py.

نفذ الخطوات خطوة بخطوة وافحص نتائج الاختبارات.
```

## 13. الاختبارات المطلوبة

- اختبار إرسال واستقبال `TEXT_MESSAGE` بين مستخدمين بلغات مختلفة والتأكد من الترجمة الصحيحة.
- اختبار إرسال رسالة بين مستخدمين بنفس اللغة والتأكد من `translation_source == "identity"`.
- اختبار إرسال حدث `TYPING` واستلامه من قبل الطرف الآخر.
- اختبار إرسال `HEARTBEAT` واستمرار الاتصال.
- اختبار انقطاع العميل واستلام بقية أعضاء الغرفة لحدث `LEAVE`.
- تشغيل: `pytest backend/tests/websocket/ -v`

## 14. شروط نجاح المهمة

- استلام كل مستخدم للرسالة مترجمة بلغته المفضلة بدقة متناهية.
- تسليم النص الأصلي دائماً مع المترجم.
- بث أحداث الانضمام والمغادرة والكتابة بسلاسة.
- نجاح 100% لاختبارات الويب سوكت والتكامل.

## 15. شروط عدم النجاح

- عدم ترجمة الرسالة للغة المتلقي.
- انهيار الاتصال عند فشل الترجمة.
- عدم إرسال حدث `LEAVE` عند خروج المستخدم.

## 16. ممنوعات قطعية

- ممنوع تعديل ملفات الترجمة أو الموديلز مباشرة من طرفك.
- ممنوع تغيير هيكل استجابة الرسالة.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Mohammed/DELIVERY/DELIVERY-TASK-04.md`.
3. الصق تقرير نتائج الاختبارات الكامل في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد باكتمال منظومة الويب سوكت والاتصال الفوري بنجاح 100% لتسهيل ربط خطافات `useWebSocket` وواجهات الـ Frontend.
