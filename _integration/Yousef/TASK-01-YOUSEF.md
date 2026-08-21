# إعداد قاعدة البيانات ونماذج الجداول الأساسية (Database Setup & Models)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-01-YOUSEF`
- **العضو المسؤول**: يوسف خيري
- **الدور**: مهندس قواعد البيانات والـ Backend
- **الحالة**: جاهزة للتنفيذ (Ready to Start)
- **الأولوية**: حرجة جداً (Critical - Foundation)

## 2. هدف المهمة

بناء وتهيئة البنية التحتية لقاعدة البيانات (PostgreSQL) باستخدام SQLAlchemy Async ونظام إدارة الجلسات غير المتزامن (Async Session Management)، والتأكد من تعريف النماذج الوراثية الأساسية (Base Models) ومولدات المعرفات الفريدة (UUID) بدقة تطابق المخطط الرسمي المعتمد.

## 3. لماذا هذه المهمة؟

قاعدة البيانات هي حجر الأساس الذي تعتمد عليه كافة الخدمات الأخرى في LinguaChat (المستخدمين، الغرف، العضويات، الرسائل المحفوظة، وإحصائيات لوحة التحكم). بدون إعداد صحيح لجلسات الاتصال غير المتزامنة ونماذج الجداول، لن تتمكن بقية الوحدات من العمل.

## 4. اقرأ هذه الملفات أولاً

- `docs/database-schema.md` (المصدر الأساسي للحقيقة لمخطط الجداول والحقول والقيود والفهارس)
- `docs/architecture.md` (القسم 3.7 وقواعد الفصل بين الطبقات)
- `docs/security.md` (القسم 1 و 9 الخاص بأمان قاعدة البيانات)
- `backend/app/core/config.py` (متغيرات البيئة والاتصال `DATABASE_URL`)

## 5. الملفات المسموح تعديلها

- `backend/app/database/base.py`
- `backend/app/database/session.py`
- `backend/app/database/models/__init__.py`
- `backend/app/database/models/user.py`
- `backend/app/database/models/room.py`
- `backend/app/database/models/room_member.py`
- `backend/app/database/models/message.py`
- `backend/app/database/models/translation.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/translation/**` (خاص بمؤيد الصوفي)
- `frontend/**` (خاص بأحمد العماري)
- كافة ملفات `docs/**` (لا تعدل العقود)

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_database.py` (لاختبار الاتصال والنماذج)

## 8. المتطلبات الوظيفية

1. **محرك الاتصال غير المتزامن (Async Engine)**: إنشاء `create_async_engine` باستخدام `DATABASE_URL` من `core.config.settings`.
2. **مصنع الجلسات (Async Sessionmaker)**: إنشاء `async_sessionmaker` مع تعطيل `expire_on_commit=False`.
3. **مزود الجلسات (Dependency `get_db`)**: دالة مولدة غير متزامنة توفر جلسة `AsyncSession` وتضمن إغلاقها بأمان في كتلة `finally`.
4. **النماذج الأساسية (Declarative Base)**: تعريف الـ `Base` مع دعم الحقول المشتركة والـ Type Annotations الحديثة في SQLAlchemy 2.0.
5. **مطابقة الحقول الخمسة للجداول**:
   - `users`: `id` (UUID PK), `username` (VARCHAR 50 UNIQUE), `hashed_password` (VARCHAR 255), `preferred_language` (VARCHAR 10 default 'en'), `created_at` (UTC), `updated_at`, `is_active` (BOOL default TRUE).
   - `rooms`: `id` (UUID PK), `name` (VARCHAR 100), `created_by` (UUID FK users.id ON DELETE SET NULL), `created_at` (UTC).
   - `room_members`: `id` (UUID PK), `room_id` (UUID FK rooms.id ON DELETE CASCADE), `user_id` (UUID FK users.id ON DELETE CASCADE), `joined_at` (UTC), مع قيد فريد مركب `(room_id, user_id)`.
   - `messages`: `id` (UUID PK), `room_id` (UUID FK rooms.id ON DELETE CASCADE), `sender_id` (UUID FK users.id ON DELETE SET NULL), `original_text` (TEXT NOT NULL), `original_language` (VARCHAR 10), `sent_at` (UTC).
   - `translations`: `id` (UUID PK), `message_id` (UUID FK messages.id ON DELETE CASCADE), `target_language` (VARCHAR 10), `translated_text` (TEXT NOT NULL), `provider_used` (VARCHAR 50), `confidence` (FLOAT NULLABLE), `created_at` (UTC), مع قيد فريد مركب `(message_id, target_language)`.
6. **الفهارس (Indexes)**: تضمين كافة الفهارس المذكورة في `docs/database-schema.md`.

## 9. المتطلبات غير الوظيفية

- **الأمان**: عدم السماح بأي استعلامات Raw SQL غير مفحوصة، واستخدام معاملات SQLAlchemy ORM حصراً.
- **التوقيت الزمني**: جميع حقول التوقيت يجب أن تُنشأ بنظام UTC الافتراضي (`datetime.now(timezone.utc)`).
- **إدارة الموارد**: ضبط حجم حوض الاتصالات (Connection Pool) لمنع استنزاف موارد الخادم.

## 10. Edge Cases (الحالات الطرفية)

- انقطاع الاتصال بقاعدة البيانات أثناء التهيئة (معالجة الخطأ برسالة واضحة في الـ log).
- إدخال قيم مكررة للحقول الفريدة (توليد `IntegrityError` والتعامل معها بنظام).
- حذف مستخدم قام بإنشاء غرفة (التأكد من تطبيق `ON DELETE SET NULL` على `created_by`).
- حذف غرفة تحتوي رسائل وأعضاء (التأكد من تطبيق `ON DELETE CASCADE`).

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص ملف `docs/database-schema.md` بدقة ومطابقة أنواع البيانات.
- **الخطوة 2**: فحص ملف `backend/app/core/config.py` للتأكد من قراءة `DATABASE_URL`.
- **الخطوة 3**: ضبط `backend/app/database/session.py` لإنشاء الـ `engine` والـ `sessionmaker` ودالة `get_db`.
- **الخطوة 4**: مراجعة وإكمال ملفات النماذج داخل `backend/app/database/models/` والتأكد من استيرادها في `__init__.py`.
- **الخطوة 5**: إنشاء ملف اختبار `backend/tests/unit/test_database.py` للتحقق من سلامة تعريف الجداول وعلاقاتها.
- **الخطوة 6**: تشغيل الاختبارات باستخدام `pytest backend/tests/unit/test_database.py`.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-01-YOUSEF (إعداد قاعدة البيانات ونماذج الجداول الأساسية).

قبل التنفيذ اقرأ الملفات التالية:
- docs/database-schema.md
- docs/architecture.md
- docs/security.md
- backend/app/core/config.py

لا تنشئ مشروعًا جديدًا.
لا تغير Architecture.
لا تغير Contracts أو أسماء الجداول أو الحقول.
لا تعدل ملفات خارج نطاق قاعدة البيانات:
الملفات المسموح لك بتعديلها:
- backend/app/database/base.py
- backend/app/database/session.py
- backend/app/database/models/*
- وإنشاء ملف اختبار: backend/tests/unit/test_database.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. إعداد محرك SQLAlchemy Async ومولد الجلسات ودالة get_db في database/session.py.
2. تعريف نماذج الجداول الخمسة بالكامل طبقاً لـ docs/database-schema.md:
   - User في models/user.py
   - Room في models/room.py
   - RoomMember في models/room_member.py
   - Message في models/message.py
   - Translation في models/translation.py
3. التأكد من القيود الفريدة (Unique Constraints) والعلاقات وحذف المفاتيح الخارجية (Cascade / Set Null).
4. كتابة اختبار في backend/tests/unit/test_database.py يتحقق من صحة المخطط والجداول.

نفذ المهمة خطوة بخطوة، وشغل الاختبارات، وتأكد من خلو الكود من الأخطاء.
```

## 13. الاختبارات المطلوبة

- اختبار إنشاء جلسة قاعدة البيانات غير المتزامنة والتأكد من نوعها (`AsyncSession`).
- اختبار سلامة مخطط الجداول والتحقق من وجود جميع الأعمدة والقيود (Constraints).
- تشغيل: `pytest backend/tests/unit/test_database.py`

## 14. شروط نجاح المهمة

- كافة نماذج الجداول الخمسة مطابقة 100% لـ `docs/database-schema.md`.
- دالة `get_db` تعمل كمولد (async generator) بدون تسريب للاتصالات.
- جميع اختبارات الوحدة تمر بنجاح (100% Pass).

## 15. شروط عدم النجاح (متى تتوقف؟)

- إذا كان هناك نقص في نوع بيانات عمود أو قيد أجنبي (FK) محدد في العقد.
- إذا فشلت اختبارات SQLAlchemy مع ظهور خطأ في تعريف العلاقات.
- إذا تم استخدام مكتبة متزامنة (Sync) بدل غير المتزامنة (Async).

## 16. ممنوعات قطعية

- ممنوع إضافة جداول جديدة غير موجودة في `docs/database-schema.md`.
- ممنوع تغيير أسماء الحقول أو أنواعها.
- ممنوع تخزين كلمات المرور كنص صريح في أي مكان.
- ممنوع كتابة استعلامات Raw SQL.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Yousef/DELIVERY/DELIVERY-TASK-01.md`.
3. املأ تقرير التسليم بنتائج الاختبارات الحقيقية والتفاصيل.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجاهزية نماذج قاعدة البيانات وجلسات الاتصال غير المتزامنة.
- تأكيد أن جميع الحقول والجداول مطابقة للعقد ولا يوجد أي نقص.
