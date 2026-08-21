# 04 - بناء مدير اتصالات الويب سوكت (04_CONNECTION_MANAGER)

## الهدف
بناء وتطوير فئة `ConnectionManager` في `backend/app/websocket/manager.py` لإدارة اتصالات الغرف المتزامنة في الذاكرة، وتتبع الاتصالات النشطة، وتوزيع الرسائل (Broadcast).

## اقرأ أولًا
- `team_package/contracts/WEBSOCKET_CONTRACT.md`
- `backend/app/websocket/manager.py`

## الملفات المسموح تعديلها
- `backend/app/websocket/manager.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `team_package/**`

## المتطلبات الوظيفية
1. إدارة قواميس الاتصالات لكل غرفة: `room_id -> user_id -> {"ws": WebSocket, "user": dict, "last_heartbeat": float}`.
2. دالة `connect(room_id, user_id, user_data, websocket)`: قبول وتسجيل الاتصال.
3. دالة `disconnect(room_id, user_id)`: إزالة الاتصال وتنظيف الغرفة.
4. دالة `broadcast_to_room(room_id, message, exclude_user_id)`: إرسال الرسائل لكافة أعضاء الغرفة.
5. دالة `record_heartbeat(room_id, user_id)`: تحديث توقيت آخر نبضة.
6. دالة `get_active_connections_count()`: حساب إجمالي الاتصالات النشطة.

## المتطلبات غير الوظيفية
- التعامل الآمن مع التزامن وتجنب أخطاء تعديل القواميس أثناء القراءة.
- تجاهل أخطاء الإرسال للعملاء المنقطعين وتنظيفهم دون انهيار الخادم.

## Edge Cases
- انقطاع مفاجئ لأحد العملاء أثناء البث -> تنظيف الاتصال واستمرار البث للبقية.
- إرسال لغرفة لا يوجد بها أي متصل -> عدم الانهيار وتخطي العملية بهدوء.

## خطوات التنفيذ
1. كتابة وتحديث فئة `ConnectionManager`.
2. تطبيق دوال الربط والبث والفصل والنبضات.
3. حماية العمليات بكتل معالجة الأخطاء الآمنة.

## التحقق
- فحص دوال المدير وتأكيد صحة عمليات الإضافة والحذف.

## الاختبارات
- تنفيذ `05_CONNECTION_MANAGER_TEST.md`.

## معايير النجاح
- مدير اتصالات كفؤ يعزل الغرف عن بعضها بنسبة 100%.

## شروط التوقف
- التوقف عند حدوث أي Memory Leak أو تسريب للاتصالات المغلقة.

## ممنوعات المهمة
- ممنوع مشاركة الرسائل بين غرف مختلفة.

## التسليم
- الانتقال للاختبار عبر `05_CONNECTION_MANAGER_TEST.md`.
