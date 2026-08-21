# عقد مخطط قاعدة البيانات (DATABASE_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا. يمنع تعديل أسماء الجداول أو الأعمدة أو أنواع البيانات أو القيود.

---

## 1. الجداول الرسمية (Official Tables)

1. **`users`**:
   - `id`: UUID (Primary Key)
   - `username`: VARCHAR(50), Unique, Not Null, Index
   - `hashed_password`: VARCHAR(255), Not Null
   - `preferred_language`: VARCHAR(10), Not Null, Default='en'
   - `created_at`: TIMESTAMPTZ, Not Null

2. **`rooms`**:
   - `id`: UUID (Primary Key)
   - `name`: VARCHAR(100), Not Null
   - `created_by`: UUID, Foreign Key -> users(id) ON DELETE CASCADE, Not Null
   - `created_at`: TIMESTAMPTZ, Not Null

3. **`room_members`**:
   - `id`: UUID (Primary Key)
   - `room_id`: UUID, Foreign Key -> rooms(id) ON DELETE CASCADE, Not Null
   - `user_id`: UUID, Foreign Key -> users(id) ON DELETE CASCADE, Not Null
   - `joined_at`: TIMESTAMPTZ, Not Null
   - *قيد فريد مركب*: `UNIQUE(room_id, user_id)`

4. **`messages`**:
   - `id`: UUID (Primary Key)
   - `room_id`: UUID, Foreign Key -> rooms(id) ON DELETE CASCADE, Not Null, Index
   - `sender_id`: UUID, Foreign Key -> users(id) ON DELETE CASCADE, Not Null
   - `original_text`: TEXT, Not Null
   - `original_language`: VARCHAR(10), Not Null
   - `sent_at`: TIMESTAMPTZ, Not Null, Index

5. **`translations`**:
   - `id`: UUID (Primary Key)
   - `message_id`: UUID, Foreign Key -> messages(id) ON DELETE CASCADE, Not Null, Index
   - `target_language`: VARCHAR(10), Not Null
   - `translated_text`: TEXT, Not Null
   - `provider`: VARCHAR(50), Not Null (`libretranslate`, `google`, `cache`, `identity`)
   - `confidence`: FLOAT, Nullable
   - `created_at`: TIMESTAMPTZ, Not Null
   - *قيد فريد مركب*: `UNIQUE(message_id, target_language)`
