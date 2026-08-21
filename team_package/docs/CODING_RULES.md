# معايير وقواعد كتابة الكود البرمجي (CODING_RULES.md)

تحدد هذه الوثيقة المعايير الصارمة لكتابة الأكواد في مشروع **LinguaChat**، لضمان النظافة والأداء العالي والاستقرار.

---

## 1. معايير الـ Backend (Python & FastAPI)

1. **البرمجة غير المتزامنة (Async/Await)**:
   - يجب أن تكون جميع مسارات FastAPI، واستعلامات قاعدة البيانات عبر SQLAlchemy، وعمليات استدعاء HTTP عبر `httpx.AsyncClient`، وعمليات الـ WebSocket غير متزامنة بالكامل (`async def`).
   - يمنع استخدام دوال حظر متزامنة (Blocking calls) مثل `time.sleep()` أو `requests.get()`، ويجب استخدام `asyncio.sleep()` و `httpx.AsyncClient`.
2. **تلميحات الأنواع (Type Hinting)**:
   - كتابة Type Hints كاملة لكافة الدوال والباراميترات والمخرجات.
   - استخدام Pydantic v2 Models للتحقق من كافة المدخلات والمخرجات في مسارات الـ API ورسائل الـ WebSocket.
3. **التعامل مع الأخطاء والاستثناءات (Error Handling)**:
   - التقاط الاستثناءات المحددة بدقة (Specific Exceptions) ومنع `except Exception: pass` الصامتة.
   - إرجاع استجابات الأخطاء وفق النموذج الموحد المعتمد في `contracts/API_CONTRACT.md`.
4. **عزل التبعيات (Dependency Injection)**:
   - استخدام FastAPI Dependencies لحقن جلسات قاعدة البيانات (`get_db`) والتحقق من المستخدم الحالي (`get_current_user`).

---

## 2. معايير الـ Frontend (React & Modern CSS)

1. **مكونات React الوظيفية والخطافات (Hooks)**:
   - بناء مكونات وظيفية نقية (Pure Functional Components).
   - استخدام Custom Hooks لعزل المنطق عن واجهة العرض (`useAuth`, `useWebSocket`).
2. **إدارة الحالة النظيفة (State Management)**:
   - تجنب الـ Prop Drilling واستخدام Context أو Custom Hooks.
   - تنظيف المؤقتات والاشتراكات (Cleanup functions) داخل `useEffect` لمنع تسريب الذاكرة (Memory Leaks).
3. **نظام التنسيقات (CSS System)**:
   - استخدام Vanilla CSS مع CSS Variables المنظمة داخل `frontend/src/index.css`.
   - دعم التجاوب الكامل لكافة أحجام الشاشات وتأثيرات الـ Micro-animations والـ Glassmorphism.
4. **الأمان في المتصفح**:
   - منع طباعة التوكنات وكلمات المرور في `console.log`.
   - تنظيف مدخلات المستخدم ومنع ثغرات XSS.

---

## 3. معايير قاعدة البيانات (Database & SQLAlchemy)

1. **المفاتيح الأساسية والمعرفات**:
   - استخدام UUIDv4 كمفتاح أساسي لكافة الجداول (`id`).
2. **الفهارس والقيود (Indexes & Constraints)**:
   - إضافة فهارس على الحقول المستخدمة بكثرة في البحث والربط (`user_id`, `room_id`, `created_at`, `sent_at`).
   - استخدام قيود المفاتيح الأجنبية `ForeignKey(ondelete="CASCADE")` بوضوح.
3. **الهجرات (Migrations)**:
   - أي تعديل في النماذج يجب أن يرافقه ملف هجرة Alembic مع رسالة وصفية واضحة.
