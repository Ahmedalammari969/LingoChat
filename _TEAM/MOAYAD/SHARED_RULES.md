# القواعد المشتركة لمؤيد الصوفي (SHARED_RULES.md)

1. **الالتزام بالعقود**: الالتزام الصارم بـ `_TEAM/00_SHARED/TRANSLATION_CONTRACT.md`.
2. **قاعدة الـ Identity الإلزامية**: عندما تتطابق لغة المصدر مع الهدف (`source_lang == target_lang`)، يجب إرجاع النص الأصلي مع `source_used = "identity"` و `confidence = 1.0`.
3. **حظر القيمة "none"**: يمنع منعاً باتاً استخدام أو إرجاع `"none"` في أي حقل أو رد.
4. **القيم المعتمدة لـ `source_used`**: `"libretranslate"`, `"google"`, `"cache"`, `"identity"`.
5. **إدارة الأخطاء**: تغليف كافة أخطاء المزودين في `TranslationError` وعدم تسريب استثناءات HTTP المباشرة.
