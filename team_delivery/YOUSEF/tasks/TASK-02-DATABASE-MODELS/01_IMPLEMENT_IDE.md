# برومبت التنفيذ: بناء نماذج جداول قاعدة البيانات (01_IMPLEMENT_IDE)

```text
أنت تعمل كمطور برمجيات محترف داخل مشروع: LinguaChat.
أنت تنفذ المهمة: TASK-02-DATABASE-MODELS (بناء نماذج جداول قاعدة البيانات).

قبل أي خطوة:
1. اقرأ ملف TASK.md في هذا المجلد بدقة.
2. اقرأ العقود المرتبطة في _TEAM/00_SHARED/.
3. افحص الملفات الموجودة في المستودع قبل أي تعديل.

التعليمات الصارمة:
- التزم حصرياً بالملفات المسموح بتعديلها:
  * backend/app/database/models/**
  * backend/app/database/models/__init__.py
- يمنع منعاً باتاً تعديل الملفات المحظورة:
  * frontend/**
  * backend/app/websocket/**
  * backend/app/translation/**
  * _TEAM/**
- لا تنشئ مشروعاً جديداً ولا تغير المعمارية.
- التزم بالأمان وخلو الكود من أي أسرار أو كلمات مرور.
- إذا وجدت أي تعارض أو غموض، توقف فوراً ولا تخترع حلاً وأبلغ قائد الفريق أحمد.

المطلوب تنفيذه بدقة:
- نموذج User مع UUID و username فريد و hashed_password.
- نموذج Room مع created_by و name.
- نموذج RoomMember مع قيد فريد مركب (room_id, user_id).
- نموذج Message مع original_text و original_language.
- نموذج Translation مع قيد فريد مركب (message_id, target_language).

بعد التنفيذ، أنتج تقرير IMPLEMENTATION REPORT يوضح:
- ماذا تم تنفيذه
- الملفات الجديدة والمعدلة
- الاختبارات التي تم إجراؤها
- نتائج الفحص
- ملاحظات التكامل
```
