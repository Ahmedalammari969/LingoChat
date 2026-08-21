# حزمة فريق مشروع LinguaChat المرجعية (team_package)
# READ-ONLY REFERENCE PACKAGE

> **تحذير هام جدًا**: هذا المجلد مرجعي للقراءة فقط (`READ-ONLY REFERENCE`).  
> يمنع على أي عضو من أعضاء الفريق كتابة أي كود برمجي أو تعديل أي ملف داخل `team_package/`.  
> مكان كتابة الكود الفعلي هو حصرياً في المجلدات الأصلية للمشروع: `backend/` و `frontend/`.

---

## 1. نبذة عن النظام

مشروع **LinguaChat** هو تطبيق محادثة جماعية فورية متعددة اللغات (Real-Time Multilingual Chat Application) مبني باستخدام:
- **Frontend**: React (Vite SPA) + Modern CSS + WebSocket Client.
- **Backend**: FastAPI (Python 3.11+) + SQLAlchemy Async + Pydantic v2.
- **Database**: PostgreSQL 16 + Alembic Migrations.
- **Real-Time Communication**: WebSocket Server + Connection Manager + Heartbeat.
- **Translation Engine**: LibreTranslate (Primary) + Google Translate (Fallback) + In-Memory / Redis Caching + Identity Handling.
- **Security**: JWT Authentication (Bearer) + Passlib Bcrypt (cost 12) + Strict Input Validation.

---

## 2. هيكلية الحزمة المرجعية `team_package/`

```text
team_package/
├── README.md                      # هذا الملف المرجعي
├── TEAM_START_HERE.md             # نقطة البداية الإلزامية لكل عضو
├── VERSION.md                     # توثيق الإصدارات وحالة الحزمة
│
├── docs/                          # الوثائق التأسيسية والمبادئ المشتركة
│   ├── PROJECT_CONSTITUTION.md    # دستور المشروع والقواعد الصارمة
│   ├── PROJECT_GLOSSARY.md        # قاموس المصطلحات الموحد
│   ├── PROJECT_ROLES.md           # توزيع الأدوار وحدود المسؤولية
│   ├── SYSTEM_STATES.md           # حالات النظام وتدفق البيانات
│   ├── CODING_RULES.md            # معايير كتابة الكود والجودة
│   ├── AI_DEVELOPMENT_RULES.md    # بروتوكول استخدام الذكاء الاصطناعي
│   ├── INTEGRATION_RULES.md       # قواعد الدمج والتسليم
│   └── SYSTEM_ARCHITECTURE.md     # المعمارية الشاملة وتدفق الرسائل
│
├── contracts/                     # العقود الرسمية المجمدة
│   ├── API_CONTRACT.md            # عقود مسارات REST API
│   ├── WEBSOCKET_CONTRACT.md      # عقد بروتوكول الويب سوكت
│   ├── DATABASE_CONTRACT.md       # عقد جداول ونماذج قاعدة البيانات
│   ├── TRANSLATION_CONTRACT.md    # عقد خدمات ومحركات الترجمة
│   └── SECURITY_CONTRACT.md       # عقد ومصفوفة الأمان والمصادقة
│
├── prompts/                       # البرومبتات التنفيذية والاختبارية
│   ├── TEAM_PROMPT_INDEX.md       # الفهرس الشامل لجميع البرومبتات
│   ├── shared/                    # البرومبتات المشتركة لجميع الأعضاء
│   ├── leader/                    # برومبتات وإرشادات قائد الفريق (17 ملفاً)
│   └── members/                   # برومبتات تنفيذ واختبار المهام لكل عضو
│       ├── 01_AHMED_FRONTEND/     # 19 مرحلة
│       ├── 02_MOHAMMED_WEBSOCKET/ # 19 مرحلة
│       ├── 03_MOAYAD_TRANSLATION/ # 18 مرحلة
│       └── 04_YOUSEF_BACKEND/     # 26 مرحلة
│
└── reports/                       # تقارير النظام والدمج
    └── TEAM_SYSTEM_CREATION_REPORT.md
```

---

## 3. أعضاء الفريق وحدود الملكية (Ownership Matrix)

| العضو | الدور | نطاق المسؤولية البرمجية | الملفات المملوكة |
| :--- | :--- | :--- | :--- |
| **أحمد العماري** | قائد المشروع + Frontend + Integration + Final QA | واجهات المستخدم، عميل الـ API، عميل WebSocket، التنسيقات، التنسيق الشامل، والدمج النهائي | `frontend/src/**`, `_integration/` |
| **محمد الداعس** | WebSocket Engineer | خادم الـ WebSocket، مدير الاتصالات، التحقق اللحظي، بث الأحداث، ودمج الرسائل مع الترجمة | `backend/app/websocket/**`, `backend/tests/websocket/**` |
| **مؤيد الصوفي** | Translation Engineer | كاشف اللغات، مزودو الترجمة (LibreTranslate/Google)، طبقة الكاش، وخدمة الترجمة الموحدة | `backend/app/translation/**`, `backend/tests/translation/**` |
| **يوسف خيري** | Backend / Database / REST Engineer | قاعدة البيانات، الهجرات، نماذج المستخدم والغرف والرسائل، مسارات REST، والمصادقة | `backend/app/database/**`, `backend/app/auth/**`, `backend/app/rooms/**`, `backend/app/messages/**`, `backend/app/dashboard/**`, `backend/tests/unit/**` |

---

## 4. مسار التنفيذ الإلزامي لكل عضو (Standard Lifecycle)

يجب على كل عضو اتباع التسلسل التالي بدقة متناهية في كل مهمة:

```text
READ (قراءة العقد والمهمة)
  ↓
PLAN (تخطيط الخطوات بدقة)
  ↓
IMPLEMENT (كتابة الكود في نطاق الملكية فقط)
  ↓
TEST (تشغيل الاختبارات والتحقق 100%)
  ↓
REVIEW (مراجعة ذاتية وسحابية Cloud Review)
  ↓
FIX (إصلاح أي ملاحظات أو أخطاء)
  ↓
TEST (إعادة الاختبار والتأكد من PASS)
  ↓
HANDOFF (إنشاء تقرير التسليم في _integration/<Member>/)
  ↓
STOP (التوقف وانتظار مراجعة القائد Leader Review)
```
