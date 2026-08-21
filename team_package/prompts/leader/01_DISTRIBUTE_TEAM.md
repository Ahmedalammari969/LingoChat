# خطة التوزيع الشامل للمشروع (01_DISTRIBUTE_TEAM.md)

توضح هذه الوثيقة خطة توزيع المهام والتسلسل الزمني للعمل بين أعضاء الفريق الأربعة في مشروع **LinguaChat**.

---

## 1. التوزيع الاستراتيجي والترابط المعماري

```text
[ المرحلة 1: التأسيس وقواعد البيانات والمصادقة ]
  └── Yousef Khairy (DB Foundation, Models, Security, REST Auth & Rooms)

[ المرحلة 2: محركات وكاش الترجمة ]
  └── Moayad Al-Soufi (Language Detection, LibreTranslate, Fallback, Cache, Identity)

[ المرحلة 3: محرك الاتصال الحي والويب سوكت ]
  └── Mohammed Al-Daees (WebSocket Protocol, Connection Manager, Auth, Translation & Persistence Integration)

[ المرحلة 4: واجهات المستخدم والدمج والتحقق النهائي ]
  └── Ahmed Alammari (Frontend Foundation, Auth UI, Rooms UI, Chat UI, Integration & Final QA)
```

---

## 2. مصفوفة تسليم المهام والاعتماد المتبادل

1. **يوسف** يسلم مسارات المصادقة والغرف وقواعد البيانات أولاً لدعم الـ WebSocket والـ Frontend.
2. **مؤيد** يسلم خدمة الترجمة الموحدة لدعم ترجمة الرسائل في الـ WebSocket.
3. **محمد** يربط الـ WebSocket مع خدمات يوسف ومؤيد عبر واجهاتها الرسمية.
4. **أحمد** يربط الـ Frontend مع كافة خدمات الـ REST والـ WebSocket ويشرف على التكامل النهائي.
