# 12 - بناء عميل وخطاف الـ WebSocket والـ Heartbeat (12_WEBSOCKET_CLIENT_INTEGRATION)

## الهدف
تطوير خدمة عميل الويب سوكت `frontend/src/services/websocket.js` وخطاف `frontend/src/hooks/useWebSocket.js` للاتصال المباشر بنقطة `ws://localhost:8000/ws/{room_id}?token=...` وإرسال الـ Heartbeat كل 30 ثانية وإعادة الاتصال التلقائي.

## اقرأ أولًا
- `team_package/contracts/WEBSOCKET_CONTRACT.md` (المرجع الكامل للبروتوكول)
- `team_package/contracts/SECURITY_CONTRACT.md`

## الملفات المسموح تعديلها
- `frontend/src/services/websocket.js`
- `frontend/src/hooks/useWebSocket.js`
- `frontend/src/pages/ChatPage.jsx`

## الملفات الممنوع تعديلها
- `backend/**`
- `team_package/**`

## المتطلبات الوظيفية
1. **فتح قناة الاتصال**:
   - الاتصال بـ `ws://localhost:8000/ws/{room_id}?token=${token}`.
2. **إرسال نبضات Heartbeat**:
   - إرسال رسالة `{"type": "HEARTBEAT", "payload": {}, "timestamp": "...", "room_id": "..."}` كل **30 ثانية**.
3. **إعادة الاتصال التلقائي (Exponential Backoff)**:
   - محاولة إعادة الاتصال عند الانقطاع (1s, 2s, 4s, 8s, max 30s) بحد أقصى 10 محاولات.
4. **دوال الإرسال والاستقبال**:
   - `sendMessage(text, original_language)`: إرسال `TEXT_MESSAGE`.
   - `sendTyping(is_typing)`: إرسال حدث `TYPING`.
   - معالجة واستقبال أحداث `JOIN`, `LEAVE`, `TEXT_MESSAGE`, `TYPING`, `ERROR`.

## المتطلبات غير الوظيفية
- عدم تسريب الذاكرة وتنظيف مؤقت الـ Heartbeat وقناة الاتصال عند مغادرة الصفحة.

## Edge Cases
- إغلاق الخادم للاتصال بكود 4001 أو 4003 -> عدم تكرار محاولة الاتصال وتنبيه المستخدم.
- انقطاع مؤقت لشبكة الإنترنت -> إعادة الاتصال بسلاسة.

## خطوات التنفيذ
1. كتابة خدمة `websocket.js` لدعم دورة حياة الاتصال والنبضات.
2. كتابة خطاف `useWebSocket.js` لربط الاتصال بالـ State.
3. ربط الخطاف بصفحة `ChatPage.jsx`.

## التحقق
- مراقبة تبادل رسائل الـ Heartbeat واستقبال الرسائل الحية.

## الاختبارات
- تنفيذ `13_WEBSOCKET_CLIENT_TEST.md`.

## معايير النجاح
- اتصال ويب سوكت مستقر يتطابق 100% مع `WEBSOCKET_CONTRACT.md`.

## شروط التوقف
- التوقف عند حدوث حلقات اتصال لا نهائية (Infinite Reconnect loops) في حالات الخطأ 4001/4003.

## ممنوعات المهمة
- ممنوع إرسال أي نوع رسالة غير الأنواع الستة المعتمدة.

## التسليم
- الانتقال للاختبار عبر `13_WEBSOCKET_CLIENT_TEST.md`.
