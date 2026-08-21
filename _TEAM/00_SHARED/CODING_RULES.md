# معايير كتابة الكود البرمجي (CODING_RULES.md)

تحدد هذه الوثيقة المعايير البرمجية الصارمة لكافة مطوري مشروع **LinguaChat**.

---

## 1. قواعد الـ Backend (Python & FastAPI)
- استخدام البرمجة غير المتزامنة (`async/await`) لكافة العمليات والاستعلامات.
- استخدام Type Hints كاملة ومخططات Pydantic v2 للتحقق من كافة المدخلات والمخرجات.
- معالجة الاستثناءات المحددة بدقة ومنع كتل `except Exception: pass` الصامتة.
- استخدام حقن التبعيات (FastAPI Dependency Injection) لـ `get_db` و `get_current_user`.

---

## 2. قواعد الـ Frontend (React & Modern CSS)
- مكونات وظيفية نقية (Pure Functional Components) و Custom Hooks.
- تنظيف المؤقتات والاشتراكات في `useEffect` لمنع تسريب الذاكرة.
- استخدام Vanilla Modern CSS والتصميم المتجاوب وتأثيرات Micro-animations.
- منع طباعة التوكنات وكلمات المرور في `console.log`.

---

## 3. قواعد قاعدة البيانات
- استخدام UUIDv4 كمفتاح أساسي لكافة الجداول.
- استخدام فهارس الاستعلام (Indexes) على الحقول شائعة البحث.
- كتابة وتوليد هجرات Alembic واضحة لكل تعديل.
