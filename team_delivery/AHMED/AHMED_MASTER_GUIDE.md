# دليل المطور التطبيقي الشامل: أحمد العماري (Ahmed Alammari)
# قائد المشروع + مهندس الواجهات والتكامل (Frontend & Integration Lead)

---

## 1. ما هو مشروع LinguaChat وما هي مهمتك بالضبط؟
مشروع **LinguaChat** هو تطبيق محادثة جماعية فورية متعدد اللغات. فكرته ببساطة:
مستخدم يكتب بالعربية ومستخدم آخر يقرأ بالإنجليزية وثالث بالفرنسية في نفس اللحظة مع إمكانية رؤية النص الأصلي أيضاً.

**مهمتك يا أحمد:**
أنت مسؤول عن كامل واجهات المشروع (Frontend) باستخدام **React + Vite**، وإدارة التكامل الشامل وإصدار النسخة النهائية.

---

## 2. موقعك في المعمارية الهندسية للنظام
```text
+-----------------------------------------------------------------------------------+
|  [نطاقك الحصري - AHMED]                                                           |
|  React Frontend (Vite Single Page Application)                                    |
|  - Pages: LoginPage, RoomsPage, ChatPage, DashboardPage                          |
|  - Services: apiClient (Axios/Fetch), WebSocketClient (Native WS)                 |
|  - Hooks: useAuth (Session), useWebSocket (Live Chat Events)                      |
|  - Styling: Modern CSS, Glassmorphism, Responsive Mobile & Desktop Layout         |
+--------------------------+-----------------------------------+--------------------+
                           | HTTP REST (Port 8000)             | WebSocket
                           | Header: Authorization: Bearer     | ws://.../ws/{room}?token=
                           v                                   v
+-----------------------------------------------------------------------------------+
|  [باقي الفريق - Backend / WebSocket / Translation / DB]                           |
+-----------------------------------------------------------------------------------+
```

---

## 3. حدود الملكية: ما الذي تعدله وما الممنوع لمسه؟
- ✅ **الملفات المسموح لك بتعديلها**: `frontend/src/**`, `frontend/index.html`, `frontend/package.json`, `team_delivery/AHMED/**`.
- ⛔ **الملفات الممنوع لمسها نهائياً**: `backend/**`, `docs/**`.

---

## 4. قائمة مهامك الـ 11 بالترتيب:
1. `TASK-01-FRONTEND-ANALYSIS`: قراءة وفهم متطلبات الواجهات والعقود.
2. `TASK-02-FRONTEND-FOUNDATION`: بناء ملف التنسيق العام `frontend/src/index.css`.
3. `TASK-03-API-CLIENT`: بناء عميل استدعاء الـ API وحقن JWT في `frontend/src/api/client.js`.
4. `TASK-04-AUTH-UI`: بناء شاشة تسجيل الدخول والتسجيل واختيار اللغة في `LoginPage.jsx`.
5. `TASK-05-ROOMS-UI`: بناء واجهة استعراض وإنشاء والانضمام للغرف في `RoomsPage.jsx`.
6. `TASK-06-CHAT-UI`: بناء واجهة المحادثة الحية والرسائل المترجمة في `ChatPage.jsx`.
7. `TASK-07-WEBSOCKET-CLIENT`: بناء عميل الويب سوكت والنبضات وإعادة الاتصال في `websocket.js`.
8. `TASK-08-DASHBOARD-UI`: بناء واجهة لوحة التحكم الإحصائية في `DashboardPage.jsx`.
9. `TASK-09-FRONTEND-ERROR-STATES`: تحسين حالات التحميل والأخطاء والفراغ.
10. `TASK-10-FRONTEND-FINAL-QA`: الفحص الشامل والتأكد من نجاح أمر `npm run build`.
11. `TASK-11-FINAL-INTEGRATION`: الدمج الشامل وتدقيق حزمة التسليم النهائية.

---

## 5. خطوات التطبيق العملي خطوة بخطوة:
1. توجه لمجلد مهمتك: `team_delivery/AHMED/tasks/TASK-XX/`.
2. اقرأ `TASK.md`.
3. انسخ محتوى `01_IMPLEMENT_IDE.md` إلى الذكاء الاصطناعي لكتابة الكود.
4. شغل أمر الاختبار من `02_TEST_IDE.md` (مثلاً: `npm run build`).
5. راجع عبر `03_EXTERNAL_AI_REVIEW.md` وتأكد من الحصول على `PASS`.
6. أنشئ تقرير التسليم داخل `handoff/` وانتقل للمهمة التالية.



## 10. المتطلبات الوظيفية وغير الوظيفية والحالات الحدية (FR, NFR & Edge Cases)
- **TASK-02 & 04 (Auth & Foundation):**
  - **FR:** تسجيل الدخول والتسجيل واختيار اللغة المفضلة، وحفظ JWT في `localStorage`.
  - **NFR:** تصميم متجاوب (Responsive)، مؤشرات تحميل فورية.
  - **Edge Cases:** كلمة مرور خاطئة (401)، اسم مستخدم مكرر (409)، حقول فارغة.
- **TASK-05 & 06 (Rooms & Chat):**
  - **FR:** إنشاء واستعراض الغرف، الانضمام، وعرض فقاعات الرسائل (المترجم والأصلي).
  - **NFR:** تمرير تلقائي وتحديث لحظي بدون وميض.
  - **Edge Cases:** رسائل طويلة جداً، نصوص رموز تعبيرية فقط، مستخدم غير منضم.
- **TASK-07 & 08 (WS & Dashboard):**
  - **FR:** ربط خطاف WebSocket، إرسال نبضات Heartbeat كل 30 ثانية، ومقاييس الداشبورد.
  - **NFR:** إعادة الاتصال التلقائي (Exponential Backoff).
  - **Edge Cases:** انقطاع مفاجئ للاتصال، استلام رسالة ERROR، توكن منتهي الصلاحية.

## 11. دليل حل وتصحيح المشاكل الشائعة فوراً (Troubleshooting Guide)
1. **خطأ CORS عند الاتصال بالـ Backend:** تفعيل الـ Proxy في `vite.config.js` لمسار `/api` إلى `http://localhost:8000`.
2. **تكرار اتصال الـ WebSocket وتجمد المتصفح:** ضبط مصفوفة التبعيات `[roomId, token]` في `useEffect` مع دالة تنظيف `ws.close()`.
3. **انتهاء توكن JWT:** إضافة Interceptor في `api/client.js` يمسح التوكن عند استلام `401` ويعيد التوجيه لـ `/login`.
