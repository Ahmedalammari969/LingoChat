"""
backend/app/translation/errors.py
TASK-07: تعريف استثناءات خدمة الترجمة
TRANSLATION_CONTRACT.md — يُحظر تسريب أخطاء HTTP للمستهلكين
"""


class ProviderError(Exception):
    """
    استثناء داخلي يُرفع من أي مزود (LibreTranslate أو Google).
    لا يُكشف مباشرةً لمستهلكي الخدمة (WebSocket / REST).
    يُستخدم داخلياً للتنقل بين المزودين وتفعيل آلية الـ Fallback.
    """

    def __init__(self, provider_name: str, reason: str):
        self.provider_name = provider_name
        self.reason = reason
        super().__init__(f"[{provider_name}] فشل المزود: {reason}")


class TranslationError(Exception):
    """
    استثناء موحد يُرفع للمستهلكين عندما تفشل جميع المزودين.
    يُلتقط من WebSocket Router لإرسال النص الأصلي + حدث ERROR.
    يُحظر تماماً تسريب ProviderError أو أي استثناء HTTP خارج هذه الطبقة.
    """

    def __init__(self, message: str = "فشلت جميع محاولات الترجمة"):
        self.message = message
        super().__init__(message)
