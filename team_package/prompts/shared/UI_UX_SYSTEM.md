# معايير نظام واجهة وتجربة المستخدم (UI_UX_SYSTEM.md)

تحدد هذه الوثيقة مواصفات التصميم المرئي والجمالي لتطبيق **LinguaChat**، والتي يجب على مهندس الواجهات أحمد العماري تطبيقها.

---

## 1. الفلسفة البصرية (Visual Philosophy)

1. **الجاذبية والأناقة الفورية (Rich Modern Aesthetics)**:
   - واجهة مذهلة وعصرية تمنح المستخدم انطباعاً بالجودة العالية من النظرة الأولى.
   - استخدام تدرجات لونية ناعمة، ولمسات زجاجية حديثة (Glassmorphism)، وتأثيرات ضوئية خفيفة.
2. **الخطوط والطباعة (Modern Typography)**:
   - خطوط عصرية واضحة تدعم اللغتين العربية والإنجليزية بشكل متناسق.
   - تباين عالي للنصوص للقراءة المريحة.
3. **الحيوية والتفاعل (Micro-animations & Fluid UX)**:
   - تأثيرات ناعمة عند التمرير بالفأرة (Hover effects).
   - انتقالات سلسة للرسائل المنبثقة ومؤشرات التحميل وأزرار التفاعل.
4. **التجاوب الكامل (Responsive Layouts)**:
   - تجربة متكاملة على شاشات الهواتف المحمولة والأجهزة اللوحية والشاشات العريضة.

---

## 2. لوحة الألوان المعتمدة (Design Tokens)

```css
:root {
  /* Brand Palette */
  --color-primary: #6366f1;         /* Indigo */
  --color-primary-hover: #4f46e5;
  --color-secondary: #06b6d4;       /* Cyan */
  --color-accent: #8b5cf6;          /* Purple */

  /* Neutral Backgrounds */
  --bg-main: #0f172a;               /* Dark Slate */
  --bg-surface: #1e293b;            /* Slate Card */
  --bg-surface-glass: rgba(30, 41, 59, 0.75);

  /* Status Colors */
  --color-success: #10b981;         /* Emerald */
  --color-warning: #f59e0b;         /* Amber */
  --color-danger: #ef4444;          /* Rose */
  --color-info: #3b82f6;            /* Blue */

  /* Typography */
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
}
```
