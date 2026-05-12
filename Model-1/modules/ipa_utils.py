"""Small utilities for IPA handling used across modules."""
import re


def normalize_ipa(s: str) -> str:
    """Remove stress markers and whitespace from an IPA string.

    Keeps normalization consistent across modules.
    """
    if not s:
        return ""
    return re.sub(r"[ˈˌ\u02C8\u02CC\s]", "", s)
