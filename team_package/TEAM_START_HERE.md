# دليل البدء السريع لأعضاء الفريق (TEAM_START_HERE.md)

مرحبًا بك في فريق عمل مشروع **LinguaChat**!

هذا الدليل هو نقطتك الأولى لفهم كيفية استخدام هذه الحزمة المرجعية وتنفيذ مهامك بأعلى درجات الدقة والاحترافية.

---

## 1. القواعد الجوهرية قبل كتابة أي سطر كود

1. **حزمة `team_package/` للقراءة فقط (READ-ONLY)**:
   - لا تعدل أي ملف داخل `team_package/`.
   - لا تنشئ ملفات كود داخل `team_package/`.
   - الكود يكتب حصرياً في `backend/` و `frontend/`.
2. **الالتزام بالملكية (Ownership Boundaries)**:
   - لا تلمس أي ملف يقع خارج نطاق مسؤوليتك الصريحة.
   - إذا احتجت وظيفة من زميلك، استخدم الواجهة البرمجية (Interface/Contract) المعتمدة.
3. **العقود مقدسة ومجمدة (Frozen Contracts)**:
   - يمنع تعديل أي Endpoint، أو حقل JSON، أو اسم عمود في قاعدة البيانات، أو نوع رسالة WebSocket.
4. **التوقف الفوري عند التعارض (Stop on Conflict)**:
   - إذا وجدت أي تناقض بين الكود والعقود، توقف فوراً وأبلغ قائد المشروع **أحمد العماري**.

---

## 2. كيف تبدأ العمل كعضو في الفريق؟

### الخطوة 1: تعرف على دورك
افتح ملف [PROJECT_ROLES.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/docs/PROJECT_ROLES.md) وتعرف على مسؤولياتك والملفات المسموح لك بتعديلها والملفات الممنوعة عليك قطعيًا.

### الخطوة 2: راجع العقود الخاصة بك
افتح مجلد [team_package/contracts/](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/) واقرأ العقود ذات الصلة بمهامك:
- يوسف خيري: [DATABASE_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/DATABASE_CONTRACT.md) و [API_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/API_CONTRACT.md) و [SECURITY_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/SECURITY_CONTRACT.md).
- مؤيد الصوفي: [TRANSLATION_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/TRANSLATION_CONTRACT.md).
- محمد الداعس: [WEBSOCKET_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/WEBSOCKET_CONTRACT.md).
- أحمد العماري: كافة العقود مع التركيز على [API_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/API_CONTRACT.md) و [WEBSOCKET_CONTRACT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/contracts/WEBSOCKET_CONTRACT.md).

### الخطوة 3: افتح برومبتات مهامك
توجه إلى مجلد مهامك داخل `team_package/prompts/members/`:
- أحمد: `01_AHMED_FRONTEND/`
- محمد: `02_MOHAMMED_WEBSOCKET/`
- مؤيد: `03_MOAYAD_TRANSLATION/`
- يوسف: `04_YOUSEF_BACKEND/`

### الخطوة 4: مسار تنفيذ المهمة
لكل مهمة من مهامك:
1. افتح ملف `XX_TASK_NAME_EXECUTE.md`.
2. انسخ المحتوى إلى الذكاء الاصطناعي في IDE.
3. نفذ المطلوب وافحص الكود.
4. افتح ملف `XX_TASK_NAME_TEST.md` وشغل الاختبارات.
5. تأكد من نجاح الاختبارات بنسبة 100% (PASS).
6. قم بعمل مراجعة سحابية باستخدام [CLOUD_REVIEW_PROMPT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/prompts/shared/CLOUD_REVIEW_PROMPT.md).
7. أنشئ تقرير التسليم داخل `_integration/<YourName>/TASK-XX-<YOURNAME>.md` باتباع [HANDOFF_INSTRUCTIONS.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/prompts/shared/HANDOFF_INSTRUCTIONS.md).
8. **توقف (STOP)** وأبلغ قائد المشروع للمراجعة والاعتماد.
