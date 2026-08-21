# حزمة الاختبارات الشاملة للـ Backend (REST Unit & Integration Suite)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-07-YOUSEF`
- **العضو المسؤول**: يوسف خيري
- **الدور**: مهندس قواعد البيانات والـ Backend
- **الحالة**: جاهزة للتنفيذ بعد إكمال المهام 01 إلى 06
- **الأولوية**: عالية (High)

## 2. هدف المهمة

بناء وتشغيل حزمة الاختبارات الشاملة (Unit & Integration Tests) لكافة مسارات الـ REST API ووحدات قواعد البيانات والمصادقة، والتأكد من تغطية جميع سيناريوهات النجاح والخطأ وحالات الـ Edge Cases المعتمدة في العقود.

## 3. لماذا هذه المهمة؟

التأكد من خلو الـ Backend من أي ثغرات أو أخطاء تكامل قبل تسليمه للدمج مع واجهات المستخدم (Frontend) وخدمات الاتصال الحي (WebSocket).

## 4. اقرأ هذه الملفات أولاً

- `docs/api-contract.md` (التحقق من جميع الأكواد ورموز الاستجابات 200, 201, 400, 401, 403, 404, 409, 422)
- `docs/security.md` (قائمة التحقق الأمني)
- `backend/pytest.ini` (إعدادات بيئة الاختبار)
- `backend/tests/test_smoke.py`

## 5. الملفات المسموح تعديلها

- `backend/tests/unit/**` (خاص بوحدات DB, Auth, Users, Rooms, Messages, Dashboard)
- `backend/tests/integration/test_api_integration.py`
- `backend/tests/conftest.py` (إن وجد لتهيئة قاعدة البيانات المؤقتة SQLite/PostgreSQL للـ Tests)

## 6. الملفات الممنوع تعديلها

- `backend/tests/websocket/**` (خاص بمحمد الدعيـس)
- `backend/tests/unit/test_translation*` (خاص بمؤيد الصوفي)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/integration/test_api_integration.py`
- `backend/tests/conftest.py`

## 8. المتطلبات الوظيفية

1. **إعداد بيئة الاختبار المشتركة (`conftest.py`)**:
   - إعداد Test Client غير متزامن (`httpx.AsyncClient` أو `TestClient`).
   - إعداد Fixtures لإنشاء قاعدة بيانات اختبارية مؤقتة وتفريغها بعد كل اختبار.
   - إعداد Fixtures لتوليد مستخدمين وتوكنات JWT صالحة ومنتهية ومزورة.
2. **اختبارات التكامل الشاملة (`test_api_integration.py`)**:
   - سيناريو 1: دورة حياة المستخدم الكاملة (Register -> Login -> استلام التوكن).
   - سيناريو 2: دورة حياة الغرفة (إنشاء غرفة -> التحقق من وجود المنشئ في الأعضاء -> انضمام مستخدم آخر -> رفض انضمام مكرر).
   - سيناريو 3: دورة حياة الرسائل وتاريخ المحادثة (إرسال رسائل -> جلب السجل -> التحقق من الترقيم ومنع غير الأعضاء).
   - سيناريو 4: فحص لوحة الإحصائيات بعد تنفيذ العمليات والتحقق من زيادة العدادات.

## 9. المتطلبات غير الوظيفية

- **السرعة والاستقلالية**: أن تعمل الاختبارات بسرعة وبشكل معزول دون التأثير على بيانات التطوير الفعلية.
- **التغطية الشاملة**: تغطية كافة حالات الأخطاء (400, 401, 403, 404, 409, 422).

## 10. Edge Cases (الحالات الطرفية)

- إرسال طلبات متزامنة في نفس اللحظة للتأكد من عدم حدوث Deadlock.
- محاولة تجاوز الترقيم بأرقام ضخمة جداً.
- فحص استجابة الـ Endpoints عند إرسال JSON مشوه أو حقول غير متوقعة.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص ملفات الاختبارات الحالية في `backend/tests/unit/`.
- **الخطوة 2**: إنشاء/تحديث `backend/tests/conftest.py` لتهيئة الـ fixtures.
- **الخطوة 3**: كتابة سيناريوهات التكامل في `backend/tests/integration/test_api_integration.py`.
- **الخطوة 4**: تشغيل الفحص الكامل لكافة اختبارات الـ REST API.
- **الخطوة 5**: جمع مخرجات الاختبارات والتحقق من عدم وجود أي Failures.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-07-YOUSEF (حزمة الاختبارات الشاملة للـ Backend REST).

قبل التنفيذ اقرأ الملفات التالية:
- docs/api-contract.md
- docs/security.md
- docs/architecture.md
- backend/pytest.ini

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها أو إنشائها:
- backend/tests/unit/test_auth.py
- backend/tests/unit/test_rooms.py
- backend/tests/unit/test_messages.py
- backend/tests/unit/test_dashboard.py
- backend/tests/unit/test_database.py
- backend/tests/unit/test_security.py
- backend/tests/integration/test_api_integration.py
- backend/tests/conftest.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. إعداد conftest.py لتوفير AsyncClient وقاعدة بيانات للاختبارات.
2. التأكد من تغطية كافة المسارات (Auth, Rooms, Messages, Dashboard, Health) بجميع حالات النجاح والأخطاء.
3. كتابة اختبارات تكامل في test_api_integration.py تختبر التدفق الطبيعي الكامل من التسجيل إلى تبادل الرسائل.
4. تشغيل pytest والتأكد من نجاح جميع الاختبارات 100%.

نفذ وشغل الاختبارات وسجل المخرجات بدقة.
```

## 13. الاختبارات المطلوبة

- تشغيل: `pytest backend/tests/unit/ -v`
- تشغيل: `pytest backend/tests/integration/test_api_integration.py -v`
- تشغيل الفحص الكامل: `pytest backend/tests/ -v -k "not websocket and not translation"`

## 14. شروط نجاح المهمة

- نجاح 100% لجميع اختبارات الوحدة والتكامل الخاصة بـ Yousef Khairy.
- خلو المخرجات من أي Warnings حرجة أو Errors.

## 15. شروط عدم النجاح

- وجود أي اختبار فاشل (Failed test).
- تخطي حالات الأخطاء الأمنية (401, 403, 409).

## 16. ممنوعات قطعية

- ممنوع تعديل ملفات اختبارات الـ WebSocket أو الترجمة الخاصة بزملائك.
- ممنوع تعديل كود الـ Production ليتجاوز الفحوصات الأمنية بشكل وهمي.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Yousef/DELIVERY/DELIVERY-TASK-07.md`.
3. الصق تقرير تشغيل Pytest النهائي في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بانتهاء كامل مهام الـ REST API وقواعد البيانات بنجاح وتقديم التقرير النهائي لاعتماده.
