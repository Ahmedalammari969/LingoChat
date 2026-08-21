# دليل نظام إدارة وتكامل مشروع LinguaChat (_integration)

مرحبًا بكم في نظام إدارة وتنظيم العمل البرمجي الجماعي لمشروع **LinguaChat**.
تم تصميم هذا المجلد ليكون المرجع المركزي لتنظيم وتوجيه وتتبع مهام أعضاء الفريق الأربعة وفقًا للهيكلية والعقود الرسمية المجمدة داخل `docs/`.

---

## 1. الهيكل العام لنظام التكامل والمهام

```text
_integration/
├── TEAM_WORKFLOW_AR.md     # دليل بروتوكول وسير العمل الجماعي والذكاء الاصطناعي
├── DELIVERY_TEMPLATE.md    # النموذج الرسمي الموحد لتقارير تسليم المهام
├── Ahmed/                  # مهام قائد الفريق والواجهات والتكامل النهائي
│   ├── README.md
│   ├── TASK-01-AHMED.md إلى TASK-07-AHMED.md
│   └── DELIVERY/
├── Yousef/                 # مهام قواعد البيانات و REST API والمصادقة
│   ├── README.md
│   ├── TASK-01-YOUSEF.md إلى TASK-07-YOUSEF.md
│   └── DELIVERY/
├── Mohammed/               # مهام الويب سوكت والاتصال الفوري
│   ├── README.md
│   ├── TASK-01-MOHAMMED.md إلى TASK-04-MOHAMMED.md
│   └── DELIVERY/
└── Moayad/                 # مهام خدمات ومحركات وكاش الترجمة
    ├── README.md
    ├── TASK-01-MOAYAD.md إلى TASK-04-MOAYAD.md
    └── DELIVERY/
```

---

## 2. جدول أعضاء الفريق والمسؤوليات

| العضو | الدور الأساسي | مجلد العمل | عدد المهام |
| :--- | :--- | :--- | :--- |
| **أحمد العماري (Ahmed)** | قائد الفريق + Frontend + مسؤول الدمج الشامل والاختبار النهائي | `_integration/Ahmed/` | 7 مهام |
| **يوسف خيري (Yousef)** | مهندس قواعد البيانات والـ Backend REST API والمصادقة | `_integration/Yousef/` | 7 مهام |
| **محمد الدعيـس (Mohammed)** | مهندس الاتصال الفوري والويب سوكت (WebSocket Engine) | `_integration/Mohammed/` | 4 مهام |
| **مؤيد الصوفي (Moayad)** | مهندس خدمات ومحركات الترجمة التلقائية والكاش | `_integration/Moayad/` | 4 مهام |

---

## 3. ملخص مصفوفة المهام الكاملة (22 مهمة)

### أولاً: مهام يوسف خيري (Database & REST APIs)
- [TASK-01-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-01-YOUSEF.md): تهيئة قاعدة البيانات ومحرك SQLAlchemy وتطبيق الهجرات عبر Alembic.
- [TASK-02-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-02-YOUSEF.md): نموذج المستخدم والتشفير ودوال الأمان وإدارة الجلسات.
- [TASK-03-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-03-YOUSEF.md): وحدة المصادقة والتسجيل وإصدار JWT (`/auth/register`, `/auth/login`).
- [TASK-04-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-04-YOUSEF.md): إدارة الغرف والانضمام والتحقق من العضوية (`POST/GET /rooms`, `POST /rooms/{id}/join`).
- [TASK-05-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-05-YOUSEF.md): حفظ الرسائل واسترجاع تاريخ المحادثات (`GET /rooms/{id}/messages`).
- [TASK-06-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-06-YOUSEF.md): إحصائيات لوحة التحكم ومؤشرات النظام (`GET /dashboard/stats`).
- [TASK-07-YOUSEF](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Yousef/TASK-07-YOUSEF.md): حزمة الاختبارات الشاملة للـ Backend REST.

### ثانياً: مهام مؤيد الصوفي (Translation & Caching)
- [TASK-01-MOAYAD](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Moayad/TASK-01-MOAYAD.md): وحدة كشف اللغات التلقائي (`detect_language`).
- [TASK-02-MOAYAD](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Moayad/TASK-02-MOAYAD.md): مزودو خدمة الترجمة: LibreTranslate و Google Fallback.
- [TASK-03-MOAYAD](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Moayad/TASK-03-MOAYAD.md): طبقة التخزين المؤقت للترجمة: In-Memory و Redis Fallback.
- [TASK-04-MOAYAD](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Moayad/TASK-04-MOAYAD.md): خدمة الترجمة الموحدة (`translate_message`) وقاعدة `source_used = "identity"`.

### ثالثاً: مهام محمد الدعيـس (WebSocket & Real-Time)
- [TASK-01-MOHAMMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Mohammed/TASK-01-MOHAMMED.md): بروتوكول الويب سوكت ونماذج الرسائل والتحقق (Message Envelope & Types).
- [TASK-02-MOHAMMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Mohammed/TASK-02-MOHAMMED.md): مدير اتصالات الويب سوكت ودورة الحياة والـ Heartbeat (`ConnectionManager`).
- [TASK-03-MOHAMMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Mohammed/TASK-03-MOHAMMED.md): مسار الويب سوكت والمصادقة والتحقق من العضوية (`/ws/{room_id}?token=...`).
- [TASK-04-MOHAMMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Mohammed/TASK-04-MOHAMMED.md): معالجة الرسائل الحية والتوزيع والترجمة والانقطاع.

### رابعاً: مهام أحمد العماري (Frontend & Final Integration)
- [TASK-01-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-01-AHMED.md): تهيئة بيئة الواجهات ونظام التصميم وعميل الـ API المركزي.
- [TASK-02-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-02-AHMED.md): واجهات المصادقة وإدارة الجلسات و JWT (`LoginPage.jsx`, `useAuth.js`).
- [TASK-03-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-03-AHMED.md): واجهات استعراض وإنشاء والانضمام للغرف (`RoomsPage.jsx`).
- [TASK-04-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-04-AHMED.md): واجهة المحادثة متعددة اللغات وربط الـ WebSocket (`ChatPage.jsx`, `useWebSocket.js`).
- [TASK-05-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-05-AHMED.md): واجهة لوحة التحكم ومؤشرات النظام (`DashboardPage.jsx`).
- [TASK-06-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-06-AHMED.md): الدمج الشامل والتحقق من العقود (End-to-End Integration & Audit).
- [TASK-07-AHMED](file:///d:/FOR/A/kadm/aa/linguachat/_integration/Ahmed/TASK-07-AHMED.md): الاختبارات النهائية الشاملة وحزمة التسليم (Final Testing & Release).

---

## 4. المبادئ والقواعد الصارمة

1. **الالتزام الكامل بالعقود**: العقود الموجودة في `docs/` مجمدة وملزمة، ويمنع تعديل أي Endpoint أو Schema دون إذن خطي من القائد أحمد.
2. **استخدام الذكاء الاصطناعي**: يحتوي كل ملف مهمة على قسم مخصص جاهز للنسخ (`Prompt خاص بالمهمة`) للاستخدام المباشر في IDE.
3. **التسليم والتوثيق**: يلتزم كل عضو بتسليم تقرير رسمي باستخدام [DELIVERY_TEMPLATE.md](file:///d:/FOR/A/kadm/aa/linguachat/_integration/DELIVERY_TEMPLATE.md) في مجلد `DELIVERY` الخاص به بعد اجتياز الاختبارات بنسبة 100%.
