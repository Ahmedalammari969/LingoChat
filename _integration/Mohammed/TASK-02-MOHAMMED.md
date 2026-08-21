# مدير اتصالات الويب سوكت ودورة الحياة والـ Heartbeat (Connection Manager)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-02-MOHAMMED`
- **العضو المسؤول**: محمد الدعيـس
- **الدور**: مهندس الاتصال الفوري والويب سوكت
- **الحالة**: جاهزة للتنفيذ بعد TASK-01
- **الأولوية**: حرجة (Critical)

## 2. هدف المهمة

بناء فئة `ConnectionManager` في `backend/app/websocket/manager.py` لإدارة اتصالات الغرف المتزامنة (In-Memory Room Connection Pool)، وتتبع حالة الاتصالات النشطة، ومعالجة رسائل النبضات الدورية (Heartbeat - إرسال كل 30 ثانية من العميل، وإغلاق بعد 90 ثانية من الصمت على الخادم)، وتوزيع الرسائل الفردية والجماعية (Broadcast).

## 3. لماذا هذه المهمة؟

مدير الاتصالات هو المحرك الحي الذي يحتفظ بقنوات الـ WebSocket المفتوحة لكل مستخدم داخل كل غرفة، ويضمن توجيه الرسائل اللحظية لأصحابها وعزل مستخدمي كل غرفة عن غيرها، وتنظيف الاتصالات الميتة أو المنقطعة.

## 4. اقرأ هذه الملفات أولاً

- `docs/websocket-contract.md` (القسم الخاص بـ Connection Lifecycle و HEARTBEAT و Constraints)
- `docs/architecture.md` (القسم 3.3 و 7)
- `docs/security.md` (القسم 4 و 11 الخاص بتسجيل الاتصال والانفصال)

## 5. الملفات المسموح تعديلها

- `backend/app/websocket/manager.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `backend/app/database/**` (خاص بيوسف خيري)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_websocket_manager.py`

## 8. المتطلبات الوظيفية

1. **هيكل بيانات إدارة الاتصالات**:
   - قاموس يربط معرف الغرفة `room_id` بقائمة الاتصالات النشطة أو قاموس يربط `user_id` بكائن `WebSocket` وبيانات المستخدم ولغته المفضلة:
     ```python
     # Dict[str, Dict[str, dict]] -> room_id -> user_id -> {"ws": WebSocket, "user": UserInfo, "last_heartbeat": float}
     ```
2. **دوال إدارة دورة الحياة**:
   - `connect(room_id: str, user_id: str, user_data: dict, websocket: WebSocket) -> None`:
     - قبول اتصال الويب سوكت (`await websocket.accept()`).
     - تسجيل الاتصال في الغرفة مع توقيت البداية.
   - `disconnect(room_id: str, user_id: str) -> None`:
     - إزالة الاتصال من الغرفة بأمان وتنظيف القواميس الفارغة.
   - `record_heartbeat(room_id: str, user_id: str) -> None`:
     - تحديث توقيت آخر نبضة مستلمة `last_heartbeat = time.time()`.
   - `get_active_connections_count() -> int`:
     - حساب إجمالي الاتصالات الحية لجميع الغرف (لدعم مسار الإحصائيات).
3. **دوال إرسال وتوزيع الرسائل (Messaging)**:
   - `send_personal_message(message: dict, websocket: WebSocket) -> None`: إرسال رسالة مباشرة لعميل محدد.
   - `broadcast_to_room(room_id: str, message: dict, exclude_user_id: str = None) -> None`: إرسال رسالة لجميع أعضاء الغرفة (مع إمكانية استثناء المرسل).
   - `broadcast_custom(room_id: str, message_factory_func) -> None`: إرسال رسالة مخصصة لكل عضو بحسب لغته المفضلة.
4. **مراقبة مهلة الصمت (90-second Inactivity Timeout)**:
   - آلية لفحص أو رصد الاتصالات التي لم ترسل أي رسالة أو Heartbeat لمدة 90 ثانية وإغلاقها.

## 9. المتطلبات غير الوظيفية

- **الأمان أثناء التزامن (Concurrency Safety)**: حماية القواميس المشتركة من أخطاء التعديل أثناء القراءة (`RuntimeError: dictionary changed size during iteration`).
- **المقاومة ضد انقطاع العملاء المفاجئ**: معالجة استثناءات إرسال الرسائل لعميل مغلق دون التأثير على بقية أعضاء الغرفة.

## 10. Edge Cases (الحالات الطرفية)

- محاولة العميل الاتصال بنفس الغرفة من نافذتين مختلفتين -> تحديث الاتصال أو إدارته بسلاسة.
- قطع العميل للإنترنت فجأة دون إرسال إغلاق -> اكتشاف انقطاع الاتصال عند محاولة الإرسال وتنظيف السجل.
- محاولة الإرسال لغرفة لا يوجد بها أي عضو حالياً -> عدم الانهيار وتخطي العملية بهدوء.
- إرسال Heartbeat من عميل غير مسجل في الغرفة -> تجاهله أو فصله.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص وتحديث فئة `ConnectionManager` في `backend/app/websocket/manager.py`.
- **الخطوة 2**: بناء دوال `connect`, `disconnect`, `record_heartbeat`, `broadcast_to_room`.
- **الخطوة 3**: كتابة اختبارات غير متزامنة في `backend/tests/unit/test_websocket_manager.py` باستخدام Mock WebSockets.
- **الخطوة 4**: تشغيل الاختبارات والتأكد من نجاحها الكامل.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-02-MOHAMMED (مدير اتصالات الويب سوكت ودورة الحياة والـ Heartbeat).

قبل التنفيذ اقرأ الملفات التالية:
- docs/websocket-contract.md
- docs/architecture.md
- docs/security.md

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها:
- backend/app/websocket/manager.py
- وإنشاء: backend/tests/unit/test_websocket_manager.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. بناء فئة ConnectionManager في websocket/manager.py لإدارة اتصالات الغرف.
2. توفير دوال:
   - connect(room_id, user_id, user_info, websocket)
   - disconnect(room_id, user_id)
   - record_heartbeat(room_id, user_id)
   - send_personal_message(message, websocket)
   - broadcast_to_room(room_id, message, exclude_user_id)
   - get_active_connections_count()
3. التعامل الآمن مع استثناءات الإرسال وانقطاع الاتصالات المفاجئ (Broken Connections).
4. كتابة اختبارات Mock شاملة في backend/tests/unit/test_websocket_manager.py لاختبار الانضمام، المغادرة، التوزيع، والـ Heartbeat.

نفذ الخطوات وافحص الاختبارات وتأكد من الجودة.
```

## 13. الاختبارات المطلوبة

- اختبار تسجيل وقبول اتصال عميل جديد في غرفة.
- اختبار إرسال رسالة خاصة لعميل محدد.
- اختبار توزيع رسالة (Broadcast) لجميع المتواجدين في الغرفة.
- اختبار إزالة العميل وتنظيف بيانات الغرفة عند قطع الاتصال.
- اختبار عداد الاتصالات النشطة الإجمالي.
- تشغيل: `pytest backend/tests/unit/test_websocket_manager.py`

## 14. شروط نجاح المهمة

- عزل كامل بين الغرف (الرسائل في غرفة A لا تصل إطلاقاً لغرفة B).
- استقرار النظام عند انقطاع العملاء المفاجئ.
- نجاح كافة اختبارات مدير الاتصالات بنسبة 100%.

## 15. شروط عدم النجاح

- تسريب الرسائل بين الغرف المختلفة.
- انهيار الخادم عند محاولة الإرسال لعميل مغلق.

## 16. ممنوعات قطعية

- ممنوع الاحتفاظ باتصالات مغلقة في الذاكرة (Memory Leak).
- ممنوع كسر توقيع دوال الاتصال والتوزيع.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Mohammed/DELIVERY/DELIVERY-TASK-02.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية `ConnectionManager` لبناء مسار الـ WebSocket والتحقق الأمني.
