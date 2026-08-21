# المعمارية الهندسية للنظام (SYSTEM_ARCHITECTURE.md)

توضح هذه الوثيقة المعمارية المعتمدة لنظام **LinguaChat** وتدفق البيانات بين المكونات.

---

## 1. المخطط المعماري العام

```text
React Frontend (Vite SPA)
    ├── REST API Client  ──────────► FastAPI Routers (/auth, /rooms, /messages, /dashboard)
    │                                     │
    │                                     ├── SQLAlchemy Async ORM ──► PostgreSQL 16
    │                                     │
    └── WebSocket Client ──────────► WebSocket Router (/ws/{room_id}?token=)
                                          │
                                          ├── ConnectionManager (In-Memory Pool & Heartbeat)
                                          │
                                          ├── Translation Service (translate_message)
                                          │     ├── Identity Handle (source == target -> "identity")
                                          │     ├── Cache Layer (In-Memory / Redis)
                                          │     ├── LibreTranslate (Primary Provider)
                                          │     └── Google Translate (Fallback Provider)
                                          │
                                          └── Messages Persistence Service (DB Save)
```

---

## 2. المكونات الأساسية للنظام (Core Modules)

1. **AUTH**: تسجيل المستخدمين، التحقق من كلمات المرور، إصدار وفك JWT.
2. **USERS**: إدارة بيانات المستخدم واللغة المفضلة `preferred_language`.
3. **ROOMS**: إنشاء الغرف، إدارة العضوية، وتوليد روابط الدعوة.
4. **MESSAGES**: تخزين الرسائل والترجمات واسترجاع السجلات التاريخية.
5. **WEBSOCKET**: إدارة الاتصال الحي، التحقق من JWT والعضوية، بث الأحداث الستة (`JOIN`, `LEAVE`, `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`, `ERROR`).
6. **TRANSLATION**: كشف اللغات التلقائي، الترجمة المتوازية لكل مستقبل، وإدارة الكاش والـ Identity.
7. **DASHBOARD**: تجميع إحصائيات النظام ومؤشرات الأداء.
8. **SECURITY**: التشفير، الحماية من الحقن و XSS، ومراقبة الصلاحيات.
9. **FRONTEND**: واجهات مستخدم حديثة ومتجاوبة مبنية بـ React و Modern CSS.
