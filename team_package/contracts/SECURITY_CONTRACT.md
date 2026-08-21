# عقد ومعايير الأمان الشاملة (SECURITY_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا (Frozen Contract).  
> يمنع كتابة أي أسرار في الكود أو تعطيل أي فحص أمني.

---

## 1. إدارة الأسرار والمتغيرات البيئية (Secrets Management)

- **قاعدة الصفر**: لا أسرار، ولا كلمات مرور، ولا JWT Secret Keys داخل الكود المصدري أو ملفات الاختبار أو Git.
- قراءة جميع التكوينات الحساسة من المتغيرات البيئية عبر `backend/app/core/config.py`:
  - `SECRET_KEY`: مفتاح التوقيع الرقمي للـ JWT.
  - `DATABASE_URL`: رابط الاتصال بقاعدة البيانات.
  - `LIBRETRANSLATE_API_KEY`, `GOOGLE_TRANSLATE_API_KEY`: مفاتيح مزودي الترجمة.

---

## 2. معايير تشفير كلمات المرور (Password Hashing)

- **المكتبة المعتمدة**: `passlib[bcrypt]`.
- **معامل الكلفة**: `rounds=12` (Bcrypt cost factor 12).
- **سياسة كلمات المرور**: طول لا يقل عن 8 أحرف.
- **منع تسريب كلمات المرور**: يمنع إرجاع `hashed_password` في أي استجابة API.

---

## 3. معايير مصادقة JWT (JWT Specification)

- **الخوارزمية**: `HS256`.
- **مدة الصلاحية (Expiration)**: 60 دقيقة (`ACCESS_TOKEN_EXPIRE_MINUTES = 60`).
- **حمولة التوكن (Payload Structure)**:
  ```json
  {
    "sub": "<user_id_uuid>",
    "username": "<username_string>",
    "preferred_language": "<lang_code>",
    "exp": 1755123456,
    "iat": 1755119856
  }
  ```
- **في الـ Frontend**: يتم حفظ التوكن في `localStorage.getItem('linguachat_token')` وتمريره في ترويسة `Authorization: Bearer <token>` لطلبات REST، وكـ Query Param `?token=<token>` لمصافحة الـ WebSocket.

---

## 4. سياسات التحقق من الصلاحيات (Authorization Policies)

- **عضوية الغرفة في REST**: التحقق من أن المستخدم عضو في الغرفة قبل إرجاع الرسائل السابقة (كود `403 Forbidden` إذا لم يكن عضواً).
- **عضوية الغرفة في WebSocket**: التحقق من العضوية قبل قبول الاتصال وإغلاقه بكود `4003` إذا لم يكن عضواً.

---

## 5. الحماية من الهجمات الشائعة

- **SQL Injection**: استخدام SQLAlchemy ORM المعلمة (Parameterized queries) حصراً.
- **XSS Attacks**: تنظيف مدخلات الرسائل في الـ Frontend وعدم استخدام `dangerouslySetInnerHTML`.
- **ReDoS / Buffer Overflow**: تقييد حجم رسائل الويب سوكت بـ **4096 بايت** كحد أقصى ورفض الرسائل الأكبر بكود `MESSAGE_TOO_LONG`.
