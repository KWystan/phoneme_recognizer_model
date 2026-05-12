from typing import Optional

from modules.ipa_utils import normalize_ipa

_dst = None
_init_error: Optional[Exception] = None


def _init_distance():
    global _dst, _init_error
    if _dst is not None:
        return
    try:
        from panphon.distance import Distance

        _dst = Distance()
    except Exception as e:
        _init_error = e
        _dst = None


def feature_distance(expected_phoneme: str, predicted_phoneme: str) -> float:
    """Return PanPhon feature-edit-distance between two single phonemes.

    This function initializes PanPhon's `Distance` lazily and raises a
    RuntimeError with the underlying exception if initialization fails.
    """
    _init_distance()
    if _dst is None:
        raise RuntimeError(f"PanPhon Distance initialization failed: {_init_error}")

    e = normalize_ipa(expected_phoneme)
    p = normalize_ipa(predicted_phoneme)
    return float(_dst.feature_edit_distance(e, p))


def get_feature_names():
    try:
        from panphon.featuretable import FeatureTable

        ft = FeatureTable()
        return ft.names
    except Exception:
        return []


if __name__ == "__main__":
    try:
        print("Distance b vs p:", feature_distance("b", "p"))
    except Exception as e:
        print("PanPhon init failed:", e)