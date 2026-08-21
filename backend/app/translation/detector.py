"""
LinguaChat — Language Detector (Skeleton)

Detects the language of text input.
Implementation: Moayad Al-Soufi — TASK: Translation Service
See: docs/translation-contract.md § 3. Language Detection Contract
"""


async def detect_language(text: str) -> str:
    """
    Detect the language of provided text.

    Args:
        text: Non-empty text to analyze.

    Returns:
        ISO 639-1 language code (e.g., "ar", "en", "fr").
        Returns "unknown" if detection fails — NEVER raises an exception.

    Notes:
    - Library to use: langdetect or equivalent (to be decided by Moayad Al-Soufi).
    - Must never raise exceptions; return "unknown" on any failure.
    - "unknown" must be handled gracefully by the translation service.

    See: docs/translation-contract.md § 3
    Implementation: Moayad Al-Soufi
    """
    raise NotImplementedError("Implement in translation task — Moayad Al-Soufi")
