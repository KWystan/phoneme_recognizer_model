"""Tokenize and align IPA strings, using PanPhon segments when available.

This module handles segmentation and index-wise alignment of IPA strings.
It relies on `modules.panphon_module.feature_distance` to compute per-pair
feature distances so `modules.panphon_module` remains focused on PanPhon.
"""
from typing import List, Dict, Any, Optional

from modules.panphon_module import feature_distance
from modules.ipa_utils import normalize_ipa

_segments: Optional[List[str]] = None
_init_error: Optional[Exception] = None


def _load_segments():
    """Load segment candidates from PanPhon's FeatureTable if possible.

    If loading fails, `_segments` will be set to `None` and tokenization falls
    back to single-character tokens.
    """
    global _segments, _init_error
    if _segments is not None:
        return
    try:
        from panphon.featuretable import FeatureTable

        ft = FeatureTable()
        segs = []
        if hasattr(ft, "seg_dict") and isinstance(ft.seg_dict, dict):
            segs = list(ft.seg_dict.keys())
        elif hasattr(ft, "segs"):
            segs = list(ft.segs)
        elif hasattr(ft, "segments"):
            segs = list(ft.segments)
        _segments = sorted(set(segs), key=len, reverse=True)
    except Exception as e:
        _init_error = e
        _segments = None


def tokenize_ipa(ipa: str) -> List[str]:
    s = _normalize_ipa(ipa)
    if _segments is None:
        _load_segments()
    if not _segments:
        return list(s)

    tokens: List[str] = []
    i = 0
    while i < len(s):
        matched = False
        for seg in _segments:
            if s.startswith(seg, i):
                tokens.append(seg)
                i += len(seg)
                matched = True
                break
        if not matched:
            tokens.append(s[i])
            i += 1
    return tokens


def score_ipa_sequences(expected_ipa: str, predicted_ipa: str) -> Dict[str, Any]:
    """Tokenize both inputs, align index-wise, and compute per-pair distances.

    Returns a dict with `pairs` and overall `raw_score` (average).
    """
    expected = normalize_ipa(expected_ipa)
    predicted = normalize_ipa(predicted_ipa)

    exp_tokens = tokenize_ipa(expected)
    pred_tokens = tokenize_ipa(predicted)

    n = min(len(exp_tokens), len(pred_tokens))
    pairs: List[Dict[str, Any]] = []
    total = 0.0
    for i in range(n):
        e = exp_tokens[i]
        p = pred_tokens[i]
        score = feature_distance(e, p)
        pairs.append({"index": i, "expected": e, "predicted": p, "score": float(score)})
        total += score

    raw_score = float(total / n) if n > 0 else 0.0
    return {"pairs": pairs, "raw_score": raw_score, "expected_len": len(exp_tokens), "predicted_len": len(pred_tokens)}


if __name__ == "__main__":
    print(score_ipa_sequences("bəˈnænə", "bəˈnænə"))
