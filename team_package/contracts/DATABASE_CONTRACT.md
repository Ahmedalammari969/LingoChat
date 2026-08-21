# عقد مخطط ونماذج قاعدة البيانات (DATABASE_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا (Frozen Contract).  
> يمنع تغيير أسماء الجداول، أو أنواع الحقول، أو قيود العلاقات (Foreign Keys).

---

## 1. جدول المستخدمين (`users`)

| اسم العمود | نوع البيانات | القيود | الوصف |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, default=uuid4 | المعرف الفريد للمستخدم |
| `username` | `VARCHAR(50)` | UNIQUE, NOT NULL, INDEX | اسم المستخدم الفريد (3-50 حرف) |
| `hashed_password`| `VARCHAR(255)` | NOT NULL | كلمة المرور المشفرة بـ Passlib Bcrypt |
| `preferred_language`| `VARCHAR(10)` | NOT NULL, default='en' | رمز اللغة المفضل (ISO 639-1) |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL, default=utcnow | توقيت إنشاء الحساب |

---

## 2. جدول الغرف (`rooms`)

| اسم العمود | نوع البيانات | القيود | الوصف |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, default=uuid4 | المعرف الفريد للغرفة |
| `name` | `VARCHAR(100)` | NOT NULL | اسم الغرفة |
| `created_by` | `UUID` | FOREIGN KEY -> users(id) ON DELETE CASCADE, NOT NULL | المستخدم المنشئ للغرفة |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL, default=utcnow | توقيت إنشاء الغرفة |

---

## 3. جدول أعضاء الغرف (`room_members`)

| اسم العمود | نوع البيانات | القيود | الوصف |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, default=uuid4 | معرف سجل العضوية |
| `room_id` | `UUID` | FOREIGN KEY -> rooms(id) ON DELETE CASCADE, NOT NULL | معرف الغرفة |
| `user_id` | `UUID` | FOREIGN KEY -> users(id) ON DELETE CASCADE, NOT NULL | معرف المستخدم |
| `joined_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL, default=utcnow | توقيت الانضمام للغرفة |

> **قيد فريد مركب (Composite Unique)**: `UNIQUE(room_id, user_id)` لمنع تكرار الانضمام.

---

## 4. جدول الرسائل الأصلية (`messages`)

| اسم العمود | نوع البيانات | القيود | الوصف |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, default=uuid4 | المعرف الفريد للرسالة |
| `room_id` | `UUID` | FOREIGN KEY -> rooms(id) ON DELETE CASCADE, NOT NULL, INDEX | الغرفة التابعة لها الرسالة |
| `sender_id` | `UUID` | FOREIGN KEY -> users(id) ON DELETE CASCADE, NOT NULL | معرف المرسل |
| `original_text` | `TEXT` | NOT NULL | نص الرسالة الأصلي |
| `original_language`| `VARCHAR(10)` | NOT NULL | لغة الرسالة الأصلية المكتشفة |
| `sent_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL, default=utcnow, INDEX | توقيت إرسال الرسالة |

---

## 5. جدول الترجمات (`translations`)

| اسم العمود | نوع البيانات | القيود | الوصف |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, default=uuid4 | المعرف الفريد لسجل الترجمة |
| `message_id` | `UUID` | FOREIGN KEY -> messages(id) ON DELETE CASCADE, NOT NULL, INDEX | الرسالة الأصلية المترجمة |
| `target_language` | `VARCHAR(10)` | NOT NULL | اللغة الهدف للترجمة |
| `translated_text` | `TEXT` | NOT NULL | النص بعد الترجمة |
| `provider` | `VARCHAR(50)` | NOT NULL | المزود المستخدم (`libretranslate`, `google`, `cache`, `identity`) |
| `confidence` | `FLOAT` | NULLABLE | درجة الثقة بالترجمة |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL, default=utcnow | توقيت إجراء وحفظ الترجمة |

> **قيد فريد مركب**: `UNIQUE(message_id, target_language)` لمنع تكرار ترجمة نفس الرسالة لنفس اللغة.
