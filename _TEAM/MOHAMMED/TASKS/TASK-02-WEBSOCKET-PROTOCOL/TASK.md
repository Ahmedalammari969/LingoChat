# بناء بروتوكول ونماذج رسائل الويب سوكت

## Task ID
`TASK-02-WEBSOCKET-PROTOCOL`

## العضو المسؤول
محمد الداعس (Mohammed Al-Daees) - مهندس الويب سوكت

## الهدف
بناء وتطوير نماذج التحقق من صحة رسائل الويب سوكت في backend/app/websocket/schemas.py و protocol.py للالتزام الصارم بالغلاف الموحد والحد الأقصى للحجم (4096 بايت).

## وصف المهمة
بناء وتطوير نماذج التحقق من صحة رسائل الويب سوكت في backend/app/websocket/schemas.py و protocol.py للالتزام الصارم بالغلاف الموحد والحد الأقصى للحجم (4096 بايت).

## لماذا هذه المهمة مهمة للنظام
حماية خادم الويب سوكت من الانهيار وضمان مطابقة حمولات الرسائل للعقد الرسمي.

## المتطلبات الوظيفية
- نماذج Pydantic للأنواع الستة المعتمدة.
- دوال التحقق من حجم الرسالة (<= 4096 بايت) وسلامة JSON.
- توليد رسائل الخطأ القياسية ERROR Envelope.

## المتطلبات غير الوظيفية
- سرعة معالجة عالية وخفة على الذاكرة.

## Edge Cases / الحالات الحدية
- JSON مشوه -> INVALID_JSON.
- رسالة فارغة -> EMPTY_MESSAGE.
- رسالة أكبر من 4096 بايت -> MESSAGE_TOO_LONG.

## الملفات المسموح بتعديلها
- `backend/app/websocket/schemas.py`
- `backend/app/websocket/protocol.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_websocket_protocol.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/WEBSOCKET_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `WEBSOCKET_CONTRACT.md`

## المدخلات
- الرسائل الخام المستلمة عبر WebSocket.

## المخرجات المطلوبة
- نماذج Pydantic ودوال التحقق.

## نقاط التكامل مع أعضاء الفريق
- يستخدمها WebSocket Router لفحص كافة الرسائل الواردة.

## Dependencies
- TASK-01-WEBSOCKET-ANALYSIS

## شروط اكتمال المهمة
- تطبيق دوال التحقق والنماذج بنسبة نجاح 100%.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_websocket_protocol.py -v

## طريقة التسليم
- تقرير فحص البروتوكول ونتائج الاختبارات.

## ممنوعات المهمة
- ممنوع تغيير هيكل الغلاف الموحد type, payload, timestamp, room_id.
