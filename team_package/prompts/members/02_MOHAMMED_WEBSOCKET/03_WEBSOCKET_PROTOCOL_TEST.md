# 03 - اختبار وتدقيق بروتوكول الويب سوكت (03_WEBSOCKET_PROTOCOL_TEST)

## الهدف من الاختبار
التحقق من صحة نماذج Pydantic لغلاف الرسائل والأنواع الستة واختبار دوال الفحص والتحقق من الحجم الأقصى وتوليد الأخطاء.

## الملفات الخاضعة للاختبار
- `backend/app/websocket/schemas.py`
- `backend/app/websocket/protocol.py`
- `backend/tests/unit/test_websocket_protocol.py`

## المتطلبات المسبقة
- إكمال مرحلة `02_WEBSOCKET_PROTOCOL.md`.

## حالات الاختبار (Test Cases)
1. **فحص الرسائل الصحيحة**: قبول الأنواع الستة بالهيكل الصحيح.
2. **فحص الأنواع غير المعروفة**: رفض `"type": "UNKNOWN"` بكود `UNKNOWN_MESSAGE_TYPE`.
3. **فحص الحجم الزائد**: رفض الرسائل الأكبر من 4096 بايت بكود `MESSAGE_TOO_LONG`.
4. **فحص الـ JSON المشوه**: إرجاع كود `INVALID_JSON`.
5. **فحص الرسالة الفارغة**: إرجاع كود `EMPTY_MESSAGE`.

## أوامر التشغيل
```bash
pytest backend/tests/unit/test_websocket_protocol.py -v
```

## معايير النجاح (PASS)
- نجاح 100% لكافة اختبارات البروتوكول.

## شروط الرسوب (FAIL)
- فشل أي اختبار أو قبول رسائل غير مطابقة للعقد.

## ما الذي يتم تسجيله في التقرير
- مخرجات Pytest وتفاصيل تغطية الحالات الطرفية.
