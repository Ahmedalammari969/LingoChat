# خطة توزيع مهام يوسف خيري (05_YOUSEF_DISTRIBUTION.md)

- **العضو المسؤول**: يوسف خيري (Yousef Khairy)
- **الدور**: مهندس قواعد البيانات والـ Backend REST API والمصادقة (Backend / Database / REST Engineer)
- **مجلد المهام**: `team_package/prompts/members/04_YOUSEF_BACKEND/`
- **عدد المراحل**: 26 مرحلة تفصيلية

---

## قائمة المراحل والمهام الخاصة بيوسف:

1. `01_ANALYZE_BACKEND.md`: تحليل متطلبات الـ Backend وعقود الـ REST وقاعدة البيانات.
2. `02_DATABASE_FOUNDATION.md`: إعداد محرك SQLAlchemy وجلسات الاتصال غير المتزامنة.
3. `03_DATABASE_FOUNDATION_TEST.md`: اختبار الاتصال بقاعدة البيانات وإدارة الجلسات.
4. `04_DATABASE_MODELS.md`: بناء نماذج الجداول الخمسة (users, rooms, members, messages, translations).
5. `05_DATABASE_MODELS_TEST.md`: اختبار صحة العلاقات والقيود الفريدة.
6. `06_MIGRATIONS.md`: إعداد وتوليد هجرات Alembic وتطبيقها.
7. `07_MIGRATIONS_TEST.md`: اختبار ترقية وتراجع الهجرات (Upgrade & Downgrade).
8. `08_SECURITY_FOUNDATION.md`: بناء دوال تشفير كلمات المرور وإصدار وفك رموز JWT.
9. `09_SECURITY_FOUNDATION_TEST.md`: اختبار خوارزمية التشفير والتحقق من التوكن.
10. `10_AUTH_REGISTER.md`: بناء مسار تسجيل الحساب الجديد `POST /api/v1/auth/register`.
11. `11_AUTH_REGISTER_TEST.md`: اختبار تسجيل المستخدم ومعالجة الحسابات المكررة (409).
12. `12_AUTH_LOGIN_JWT.md`: بناء مسار تسجيل الدخول وإصدار التوكن `POST /api/v1/auth/login`.
13. `13_AUTH_LOGIN_JWT_TEST.md`: اختبار تسجيل الدخول والبيانات الخاطئة (401).
14. `14_USERS.md`: بناء دالة الاعتمادية `get_current_user` وتأمين المسارات.
15. `15_USERS_TEST.md`: اختبار حماية المسارات برمز JWT.
16. `16_ROOMS.md`: بناء مسارات إنشاء واستعراض الغرف (`POST /rooms`, `GET /rooms`).
17. `17_ROOMS_TEST.md`: اختبار إنشاء واسترجاع الغرف والترقيم (Pagination).
18. `18_ROOM_MEMBERSHIP.md`: بناء مسار الانضمام ودالة التحقق من العضوية (`is_user_member_of_room`).
19. `19_ROOM_MEMBERSHIP_TEST.md`: اختبار الانضمام ومعالجة الغرفة غير الموجودة (404) والانضمام المكرر (409).
20. `20_MESSAGES.md`: بناء خدمة حفظ واسترجاع تاريخ الرسائل المترجمة `GET /rooms/{id}/messages`.
21. `21_MESSAGES_TEST.md`: اختبار استرجاع الرسائل والتحقق من عضوية الغرفة (403).
22. `22_DASHBOARD.md`: بناء مسار إحصائيات لوحة التحكم `GET /dashboard/stats`.
23. `23_DASHBOARD_TEST.md`: اختبار استخراج الإحصائيات ودقة الأرقام.
24. `24_BACKEND_INTEGRATION.md`: اختبار التكامل الشامل لمسارات الـ REST API.
25. `25_BACKEND_FINAL_QA.md`: الفحص النهائي لجودة الـ Backend ومطابقة العقود.
26. `26_BACKEND_HANDOFF.md`: إعداد تقرير التسليم النهائي للـ Backend.
