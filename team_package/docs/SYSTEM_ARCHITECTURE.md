# المعمارية الشاملة للنظام (SYSTEM_ARCHITECTURE.md)

توضح هذه الوثيقة المعمارية الهندسية لمشروع **LinguaChat**، ومكونات النظام، وحدود الطبقات، وكيفية ترابط الخدمات.

---

## 1. المخطط المعماري العام (High-Level Architecture)

```text
+-----------------------------------------------------------------------+
|                         React Frontend (SPA)                          |
|  - Pages: Login, Rooms, Chat, Dashboard                               |
|  - Hooks: useAuth, useWebSocket                                       |
|  - API Client (Axios/Fetch) + Modern CSS Design System                |
+-------------------+-------------------------------+-------------------+
                    | REST API                      | WebSocket
                    | (HTTP/JSON)                   | (ws://.../ws/{room_id}?token=)
                    v                               v
+-----------------------------------------------------------------------+
|                          FastAPI Backend                              |
|                                                                       |
|  +---------------------+  +--------------------+  +----------------+  |
|  | REST API Routers    |  | WebSocket Gateway  |  | Security / JWT |  |
|  | - /auth             |  | - /ws/{room_id}    |  | - Passlib      |  |
|  | - /rooms            |  | - ConnectionManager|  | - JWT Handler  |  |
|  | - /messages         |  | - Event Loop       |  | - Dependencies |  |
|  | - /dashboard        |  |                    |  |                |  |
|  +----------+----------+  +---------+----------+  +--------+-------+  |
|             |                       |                      |          |
|             v                       v                      v          |
|  +---------------------+  +--------------------+  +----------------+  |
|  | Service Layer       |  | Translation Service|  | Database Layer |  |
|  | - AuthService       |  | - translate_msg()  |  | - SQLAlchemy   |  |
|  | - RoomsService      |  | - detect_lang()    |  |   Async Engine |  |
|  | - MessagesService   |  | - Identity Handle  |  | - ORM Models   |  |
|  | - DashboardService  |  | - Cache Layer      |  | - Alembic      |  |
|  +----------+----------+  +---------+----------+  +--------+-------+  |
+-------------|-----------------------|----------------------|----------+
              |                       |                      |
              v                       v                      v
+-------------------------+  +-------------------+  +-------------------+
|       PostgreSQL        |  |  LibreTranslate   |  |  Redis (Optional) |
|  - users, rooms,        |  |  (Primary API)    |  |  - Translation    |
|    room_members,        |  |                   |  |    Cache Fallback |
|    messages,            |  |  Google Translate |  |                   |
|    translations         |  |  (Fallback API)   |  |                   |
+-------------------------+  +-------------------+  +-------------------+
```

---

## 2. المكونات الأساسية للنظام (System Components)

1. **وحدة المصادقة (AUTH)**: مسؤولة عن تسجيل المستخدمين الجدد والتحقق من كلمات المرور وإصدار وفك رموز JWT.
2. **وحدة المستخدمين (USERS)**: إدارة ملفات المستخدمين واللغات المفضلة.
3. **وحدة الغرف (ROOMS)**: إنشاء الغرف وتوليد روابط الدعوة والانضمام وإدارة الأعضاء.
4. **وحدة الرسائل (MESSAGES)**: حفظ الرسائل الأصلية والترجمات في قاعدة البيانات واسترجاع السجلات السابقة.
5. **وحدة الويب سوكت (WEBSOCKET)**: إدارة الاتصالات الحية المفتوحة والتحقق من التوكن والعضوية وبث الأحداث الستة.
6. **وحدة الترجمة (TRANSLATION)**: الكشف التلقائي عن اللغات، إدارة الـ Identity والكاش، وتوجيه الطلبات لـ LibreTranslate و Google Fallback.
7. **وحدة لوحة التحكم (DASHBOARD)**: تجميع إحصائيات النظام ومؤشرات الأداء في الوقت الفعلي.
8. **وحدة الأمان (SECURITY)**: التشفير، الحماية من XSS و Injection، وسياسات الصلاحيات.
9. **وحدة الواجهات (FRONTEND)**: تجربة مستخدم تفاعلية متجاوبة مبنية بـ React و Modern CSS.
