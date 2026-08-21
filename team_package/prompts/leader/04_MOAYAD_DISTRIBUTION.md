# خطة توزيع مهام مؤيد الصوفي (04_MOAYAD_DISTRIBUTION.md)

- **العضو المسؤول**: مؤيد الصوفي (Moayad Al-Soufi)
- **الدور**: مهندس خدمات ومحركات الترجمة والكاش (Translation Engineer)
- **مجلد المهام**: `team_package/prompts/members/03_MOAYAD_TRANSLATION/`
- **عدد المراحل**: 18 مرحلة تفصيلية

---

## قائمة المراحل والمهام الخاصة بمؤيد:

1. `01_ANALYZE_TRANSLATION.md`: تحليل عقد الترجمة ونطاق العمل.
2. `02_TRANSLATION_INTERFACE.md`: تعريف الواجهة المجردة `TranslationProvider`.
3. `03_TRANSLATION_INTERFACE_TEST.md`: اختبار توافق واجهة المزود.
4. `04_LANGUAGE_DETECTION.md`: بناء دالة كاشف اللغات `detect_language`.
5. `05_LANGUAGE_DETECTION_TEST.md`: اختبار كشف اللغات الشائعة والحالات الطرفية.
6. `06_LIBRETRANSLATE_PROVIDER.md`: بناء المزود الأساسي LibreTranslate ومهلة 10 ثوانٍ.
7. `07_LIBRETRANSLATE_TEST.md`: اختبار المزود الأساسي ومعالجة انقطاعه.
8. `08_GOOGLE_FALLBACK_PROVIDER.md`: بناء المزود الاحتياطي الاختياري Google Translate.
9. `09_GOOGLE_FALLBACK_TEST.md`: اختبار المزود الاحتياطي وسلوكه في غياب المفتاح.
10. `10_TRANSLATION_CACHE.md`: بناء طبقة الكاش (In-Memory + Redis Fallback).
11. `11_TRANSLATION_CACHE_TEST.md`: اختبار التخزين والاسترجاع والـ TTL والـ Cache HIT.
12. `12_IDENTITY_TRANSLATION.md`: تطبيق قاعدة تطابق اللغات وإرجاع `source_used = "identity"`.
13. `13_IDENTITY_TRANSLATION_TEST.md`: اختبار التحقق من الـ Identity ومنع القيمة "none".
14. `14_TRANSLATION_ERROR_HANDLING.md`: بناء استثناءات الترجمة الموحدة `TranslationError`.
15. `15_TRANSLATION_ERROR_TEST.md`: اختبار تغليف ومعالجة أخطاء المزودين.
16. `16_TRANSLATION_SERVICE_INTEGRATION.md`: بناء خدمة الترجمة الموحدة `translate_message`.
17. `17_TRANSLATION_FINAL_QA.md`: الفحص النهائي الشامل لمنظومة الترجمة.
18. `18_TRANSLATION_HANDOFF.md`: إعداد تقرير التسليم النهائي للترجمة.
