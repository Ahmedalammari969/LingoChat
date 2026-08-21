# 18 - الفحص النهائي الشامل لواجهات المستخدم (18_FRONTEND_FINAL_QA)

## الهدف
إجراء مراجعة وتدقيق نهائي شامل لكافة صفحات ومكونات الواجهات الأمامية والتحقق من التزامها بقائمة [FINAL_MEMBER_QA_CHECKLIST.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/prompts/shared/FINAL_MEMBER_QA_CHECKLIST.md) وخلوها من الأسرار ومطابقتها للعقود.

## اقرأ أولًا
- `team_package/prompts/shared/FINAL_MEMBER_QA_CHECKLIST.md`
- `team_package/contracts/API_CONTRACT.md`
- `team_package/contracts/WEBSOCKET_CONTRACT.md`
- `team_package/contracts/SECURITY_CONTRACT.md`

## الملفات المسموح تعديلها
- لا تعدل ملفات في هذه المرحلة إلا لإصلاح عيوب تم اكتشافها أثناء التدقيق.

## الملفات الممنوع تعديلها
- `backend/**`
- `team_package/**`

## المتطلبات الوظيفية
1. تدقيق رحلة المستخدم الكاملة في الـ Frontend:
   - Login / Register -> Rooms -> Chat (WebSocket) -> Dashboard.
2. التأكد من عدم وجود أي تسريب للتوكنات في console.log.
3. التأكد من عمل بناء الواجهة `npm run build` بنجاح تام.

## المتطلبات غير الوظيفية
- جاهزية حزمة الواجهات للإنتاج بنسبة 100%.

## Edge Cases
- فحص جميع الحالات الاستثنائية وتأكيد سلامتها.

## خطوات التنفيذ
1. مراجعة كود الواجهة بنداً بنداً.
2. تشغيل المراجعة السحابية عبر [CLOUD_REVIEW_PROMPT.md](file:///d:/FOR/A/kadm/aa/linguachat/team_package/prompts/shared/CLOUD_REVIEW_PROMPT.md).
3. التأكد من الحصول على `PASS` كامل.

## التحقق
- تشغيل بناء المشروع والتأكد من خلوه من التحذيرات.

## الاختبارات
- تنفيذ: `cd frontend && npm run build`.

## معايير النجاح
- اكتمال الواجهات ومطابقتها التامة لكافة العقود والمعايير.

## شروط التوقف
- التوقف عند وجود أي ملاحظة مصنفة كـ CRITICAL أو BLOCKER.

## ممنوعات المهمة
- ممنوع التغاضي عن أي تحذير أمني.

## التسليم
- الانتقال لإعداد تقرير التسليم النهائي عبر `19_FRONTEND_HANDOFF.md`.
