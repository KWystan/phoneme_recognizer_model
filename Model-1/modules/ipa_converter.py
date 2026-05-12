"""Simple wrapper around English->IPA conversion.

This module centralizes conversion so the rest of the code stays small and
readable. If `eng_to_ipa` is not installed, `to_ipa()` will return the input
string unchanged (caller may treat it as already-IPA).
"""
try:
    import eng_to_ipa as _eng_to_ipa
except Exception:
    _eng_to_ipa = None


def to_ipa(text: str) -> str:
    """Convert English text to IPA when possible, otherwise return text.

    Keeps the function trivial so callers don't need to handle import logic.
    """
    if not text:
        return ""
    if _eng_to_ipa:
        try:
            return _eng_to_ipa.convert(text).strip().strip("/")
        except Exception:
            return text
    return text


def available() -> bool:
    return _eng_to_ipa is not None
