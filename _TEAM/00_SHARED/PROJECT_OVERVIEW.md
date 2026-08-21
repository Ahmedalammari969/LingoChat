# نظرة عامة على مشروع LinguaChat (PROJECT_OVERVIEW.md)

مرحبًا بكم في النظام التأسيسي الموحد لمشروع **LinguaChat**.

---

## 1. ما هو مشروع LinguaChat؟

**LinguaChat** هو تطبيق محادثة جماعية فورية متعددة اللغات (Real-Time Multilingual Chat Platform)، يتيح للمستخدمين من مختلف الثقافات التواصل في غرف محادثة جماعية، بحيث يكتب كل مستخدم بلغته وتصل الرسائل لبقية المتلقين مترجمة تلقائياً إلى لغاتهم المفضلة في الوقت الفعلي مع الاحتفاظ بالنص الأصلي.

---

## 2. البنية التقنية العامة (Tech Stack)

- **الواجهة الأمامية (Frontend)**: React (Single Page Application via Vite) + Vanilla Modern CSS Design System + WebSocket Client.
- **الواجهة الخلفية (Backend)**: FastAPI (Asynchronous Python 3.11+) + Pydantic v2 + SQLAlchemy 2.0 Async.
- **قاعدة البيانات (Database)**: PostgreSQL 16 + Alembic Migrations.
- **الاتصال الفوري (Real-Time)**: WebSocket Server + Connection Manager + Heartbeat (30s client, 90s server timeout).
- **خدمات الترجمة (Translation)**:
  - كاشف اللغات التلقائي (Language Detection via ISO 639-1).
  - مزود أساسي (Primary): LibreTranslate HTTP API (10s timeout).
  - مزود احتياطي اختياري (Fallback): Google Translate API.
  - طبقة التخزين المؤقت (Cache): In-Memory Dictionary + Redis Optional Fallback.
  - آلية التطابق (Identity): إرجاع النص الأصلي فوراً مع `source_used = "identity"` و `confidence = 1.0` عند تطابق اللغات.
- **الأمان (Security)**: JWT Authentication (HS256) + Passlib Bcrypt (cost 12) + Room Membership Authorization.

---

## 3. فريق العمل والأدوار

1. **أحمد العماري (Ahmed)**: قائد المشروع + Frontend + Integration + Final QA.
2. **محمد الداعس (Mohammed)**: مهندس الاتصال الفوري والويب سوكت (WebSocket Engineer).
3. **مؤيد الصوفي (Moayad)**: مهندس خدمات ومحركات الترجمة والكاش (Translation Engineer).
4. **يوسف خيري (Yousef)**: مهندس قواعد البيانات والـ REST API والمصادقة (Backend / Database / Auth / REST Engineer).

---

## 4. المبدأ الأساسي
المشروع نظام برمجي واحد متكامل ذو كود مصدري مشترك؛ يمنع منعاً باتاً إنشاء مشاريع مستقلة أو تغيير العقود الرسمية المجمدة.
