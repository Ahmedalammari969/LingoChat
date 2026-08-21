# بناء نماذج جداول قاعدة البيانات

## Task ID
`TASK-02-DATABASE-MODELS`

## العضو المسؤول
يوسف خيري (Yousef Khairy) - مهندس الـ Backend وقواعد البيانات

## الهدف
بناء وتطوير نماذج SQLAlchemy للجداول الخمسة: users, rooms, room_members, messages, translations في backend/app/database/models/.

## وصف المهمة
بناء وتطوير نماذج SQLAlchemy للجداول الخمسة: users, rooms, room_members, messages, translations في backend/app/database/models/.

## لماذا هذه المهمة مهمة للنظام
تثبيت هيكل البيانات والعلاقات والقيود الفريدة وفقاً للعقد الرسمي.

## المتطلبات الوظيفية
- نموذج User مع UUID و username فريد و hashed_password.
- نموذج Room مع created_by و name.
- نموذج RoomMember مع قيد فريد مركب (room_id, user_id).
- نموذج Message مع original_text و original_language.
- نموذج Translation مع قيد فريد مركب (message_id, target_language).

## المتطلبات غير الوظيفية
- استخدام المفاتيح الأجنبية مع ondelete='CASCADE' والفهارس الصحيحة.

## Edge Cases / الحالات الحدية
- تكرار انضمام مستخدم لنفس الغرفة -> رفض بالقيد الفريد.

## الملفات المسموح بتعديلها
- `backend/app/database/models/**`
- `backend/app/database/models/__init__.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_database_models.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/DATABASE_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/translation/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `DATABASE_CONTRACT.md`

## المدخلات
- مواصفات جداول DATABASE_CONTRACT.md.

## المخرجات المطلوبة
- نماذج ORM متكاملة.

## نقاط التكامل مع أعضاء الفريق
- تستخدمها خدمات Auth, Rooms, Messages, Dashboard.

## Dependencies
- TASK-01-DATABASE-FOUNDATION

## شروط اكتمال المهمة
- نماذج جداول تطابق العقد الرسمي 100%.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_database_models.py -v

## طريقة التسليم
- تقرير فحص نماذج قاعدة البيانات.

## ممنوعات المهمة
- ممنوع تغيير أسماء الأعمدة أو الجداول المعرفة في العقد.
