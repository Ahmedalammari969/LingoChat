# دليل مهام المطور: مؤيد الصوفي (Moayad Al-Soufi)
# Translation, Providers & Caching Engineering Guide

> **الدور الأساسي**: مهندس خدمات الترجمة وكشف اللغات والتخزين المؤقت  
> **المسؤولية البرمجية**: Language Detection + LibreTranslate Primary + Google Translate Fallback (Optional) + In-Memory & Redis Cache + Translation Service Abstraction  
> **المستندات المرجعية الأساسية**: `docs/translation-contract.md` ، `docs/websocket-contract.md` ، `docs/security.md` ، `docs/architecture.md`

---

## 1. نطاق المسؤولية والملكية (Ownership)

### ما تملكه وتتحكم به بالكامل (Allowed Scope):
- وحدة كشف اللغات: `backend/app/translation/detector.py`.
- مزودو خدمة الترجمة: `backend/app/translation/providers.py` (`LibreTranslateProvider`, `GoogleTranslateProvider`).
- طبقة الكاش (التخزين المؤقت): `backend/app/translation/cache.py` (In-Memory Dictionary + Redis Optional Fallback).
- خدمة الترجمة الموحدة: `backend/app/translation/service.py` (`translate_message`, `detect_language`).
- استثناءات الترجمة المخصصة: `TranslationError`, `ProviderError`.
- اختبارات الترجمة: `backend/tests/unit/test_translation*`, `backend/tests/integration/test_translation*`.

### ما لا تملكه ويمنع التعديل عليه (Forbidden Scope):
- **خدمة WebSocket**: مملوكة بالكامل لزميلك **محمد الدعيـس** (`backend/app/websocket/**`).
- **قواعد البيانات وREST API**: مملوكة بالكامل لزميلك **يوسف خيري** (`backend/app/database/**`, `backend/app/auth/**`, `backend/app/rooms/**`, etc.).
- **واجهة المستخدم Frontend**: مملوكة بالكامل للقائد **أحمد العماري** (`frontend/**`).

---

## 2. خريطة تسلسل المهام (Task Sequence)

| رقم المهمة | اسم المهمة | الملفات الأساسية | الأولوية |
| :--- | :--- | :--- | :--- |
| **TASK-01-MOAYAD** | وحدة كشف اللغات التلقائي (Language Detection Module) | `translation/detector.py`, `tests/unit/test_translation_detector.py` | عالية |
| **TASK-02-MOAYAD** | مزودو الترجمة: LibreTranslate و Google Fallback (Translation Providers) | `translation/providers.py`, `tests/unit/test_translation_providers.py` | حرجة |
| **TASK-03-MOAYAD** | طبقة التخزين المؤقت: In-Memory و Redis Fallback (Translation Cache) | `translation/cache.py`, `tests/unit/test_translation_cache.py` | عالية |
| **TASK-04-MOAYAD** | خدمة الترجمة الموحدة ومعالجة الأخطاء والـ Identity (Unified Translation Service) | `translation/service.py`, `tests/unit/test_translation_service.py` | حرجة |

---

## 3. قواعد حرجة خاصة بعقد الترجمة (Critical Contract Rules)

1. **قاعدة الـ Identity الإلزامية**:
   عندما تكون لغة المصدر مساوية للغة الهدف (`source_lang == target_lang`)، يجب إعادة النص الأصلي فوراً مع تعيين:
   ```python
   "source_used": "identity"
   "confidence": 1.0
   ```
   **يمنع منعاً باتاً** استخدام أو إرجاع القيمة `"none"`.

2. **قاعدة إخفاء التفاصيل عن المستهلكين (Abstraction)**:
   مستهلكو الخدمة (مثل WebSocket Manager) يستدعون دالة `translate_message` فقط، ولا يعلمون أي مزود تم استخدامه، وتعود لهم الاستجابة الموحدة دائماً:
   ```json
   {
     "translated_text": "Hello",
     "source_used": "libretranslate",
     "confidence": 0.95
   }
   ```

3. **التعامل مع الأخطاء**:
   عند فشل جميع المزودين، يتم رفع استثناء `TranslationError` فقط، ولا يتم تسريب استثناءات المزودين الداخلية `ProviderError`.

---

## 4. إرشادات العمل اليومي واستخدام الذكاء الاصطناعي (AI Workflow)

1. افتح ملف المهمة المعنية (مثال: `TASK-01-MOAYAD.md`).
2. راجع قسم `docs/translation-contract.md`.
3. انسخ نص الـ `Prompt خاص بالمهمة` بالكامل إلى الذكاء الاصطناعي في Antigravity IDE.
4. افحص الملفات المنفذة وتأكد من عدم تسريب أي API Keys أو تغيير مسميات الحقول.
5. شغل اختبارات Pytest وتأكد من نجاحها 100%.
6. املأ تقرير التسليم في `_integration/Moayad/DELIVERY/DELIVERY-TASK-XX.md` وأبلغ القائد **أحمد العماري**.
