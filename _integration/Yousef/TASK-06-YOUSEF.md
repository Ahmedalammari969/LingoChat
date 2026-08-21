# إحصائيات لوحة التحكم ومؤشرات النظام (Dashboard Stats API)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-06-YOUSEF`
- **العضو المسؤول**: يوسف خيري
- **الدور**: مهندس قواعد البيانات والـ Backend
- **الحالة**: جاهزة للتنفيذ بعد TASK-05
- **الأولوية**: متوسطة (Medium)

## 2. هدف المهمة

تنفيذ مسار إحصائيات النظام ومؤشرات الأداء:
`GET /api/v1/dashboard/stats`
مع جلب التعداد الإجمالي للمستخدمين، الغرف، الرسائل، الترجمات، والاتصالات النشطة، مع حماية المسار بـ JWT.

## 3. لماذا هذه المهمة؟

تتيح لوحة التحكم (Dashboard) لمدير النظام والمستخدمين الاطلاع على المقاييس الحية لحجم استخدام LinguaChat وعدد العمليات والترجمات المنجزة.

## 4. اقرأ هذه الملفات أولاً

- `docs/api-contract.md` (القسم 7 الخاص بـ `GET /dashboard/stats`)
- `docs/database-schema.md` (جداول `users`, `rooms`, `messages`, `translations`)
- `docs/architecture.md` (القسم 3.4 و 4 الخاص بحدود وحدة Dashboard)

## 5. الملفات المسموح تعديلها

- `backend/app/dashboard/service.py`
- `backend/app/dashboard/router.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_dashboard.py`

## 8. المتطلبات الوظيفية

1. **مسار `GET /api/v1/dashboard/stats`**:
   - حماية عبر Bearer JWT (إرجاع 401 عند غياب التوكن).
   - إجراء استعلامات تجميعية سريعة (Count Queries) لجلب:
     - `total_users`: إجمالي عدد المستخدمين المسجلين في جدول `users`.
     - `total_rooms`: إجمالي عدد الغرف المنشأة في جدول `rooms`.
     - `total_messages`: إجمالي عدد الرسائل المرسلة في جدول `messages`.
     - `total_translations`: إجمالي عدد الترجمات المسجلة في جدول `translations`.
     - `active_connections`: عدد الاتصالات النشطة حالياً (استرجاع العدد من مدير الاتصالات أو إرجاع 0 كقيمة افتراضية آمنة).
   - إرجاع استجابة `200 OK`:
     ```json
     {
       "total_users": 0,
       "total_rooms": 0,
       "total_messages": 0,
       "total_translations": 0,
       "active_connections": 0
     }
     ```

## 9. المتطلبات غير الوظيفية

- **الأداء**: استعلامات قراءة فقط (Read-Only Aggregations) عالية السرعة وخفيفة على قاعدة البيانات.
- **الأمان**: عدم كشف أي بيانات شخصية للمستخدمين، وتوفير أرقام إحصائية مجردة فقط.

## 10. Edge Cases (الحالات الطرفية)

- قاعدة البيانات جديدة وفارغة (إرجاع جميع الأرقام أصفار 0 دون حدوث Null Pointer أو أخطاء).
- طلب الإحصائيات مع توكن منتهي الصلاحية -> 401 Unauthorized.
- بطء استعلام العد في حال وجود ملايين السجلات -> استخدام `func.count(Model.id)` المحسن.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص مسار `backend/app/dashboard/service.py` وبناء دوال العد التجميعي.
- **الخطوة 2**: كتابة وتأمين مسار `backend/app/dashboard/router.py` باستخدام `get_current_user`.
- **الخطوة 3**: كتابة اختبارات المسار في `backend/tests/unit/test_dashboard.py`.
- **الخطوة 4**: تشغيل الاختبارات والتأكد من نجاحها.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-06-YOUSEF (إحصائيات لوحة التحكم ومؤشرات النظام).

قبل التنفيذ اقرأ الملفات التالية:
- docs/api-contract.md (القسم 7 الخاص بـ /dashboard/stats)
- docs/database-schema.md
- docs/architecture.md

لا تنشئ مشروعًا جديدًا.
لا تغير اسم الـ Endpoint أو مفاتيح الـ JSON في الاستجابة.
الملفات المسموح لك بتعديلها:
- backend/app/dashboard/service.py
- backend/app/dashboard/router.py
- وإنشاء: backend/tests/unit/test_dashboard.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. بناء خدمة dashboard/service.py لاستخراج إحصائيات:
   - total_users
   - total_rooms
   - total_messages
   - total_translations
   - active_connections
2. تطبيق مسار GET /api/v1/dashboard/stats وتأمينه بـ JWT مع إرجاع 200 OK.
3. معالجة حالة قاعدة البيانات الفارغة بإرجاع الأصفار.
4. كتابة اختبارات شاملة في backend/tests/unit/test_dashboard.py.

نفذ الخطوات وافحص الاختبارات.
```

## 13. الاختبارات المطلوبة

- اختبار استدعاء `/dashboard/stats` بتوكن صالح والتحقق من صحة مفاتيح الـ JSON.
- اختبار رفض الوصول دون توكن بكود 401.
- اختبار دقة الأرقام الإحصائية ومطابقتها للسجلات الحقيقية في قاعدة البيانات.
- تشغيل: `pytest backend/tests/unit/test_dashboard.py`

## 14. شروط نجاح المهمة

- تطابق كامل لمخرجات المسار مع `docs/api-contract.md`.
- نجاح كافة اختبارات لوحة التحكم بنسبة 100%.

## 15. شروط عدم النجاح

- غياب أي حقل من الحقول الخمسة المطلوبة في الاستجابة.
- السماح بالوصول دون مصادقة JWT.

## 16. ممنوعات قطعية

- ممنوع تعديل أسماء الحقول الإحصائية أو إرجاع قيم نصية بدلاً من أرقام صحيحة `int`.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Yousef/DELIVERY/DELIVERY-TASK-06.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية مسار الإحصائيات لربطه مع صفحة `DashboardPage.jsx` في الـ Frontend.
