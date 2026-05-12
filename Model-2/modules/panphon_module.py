from panphon.distance import Distance
from difflib import SequenceMatcher

dst = Distance()
STRICTNESS_MULTIPLIER = 3.0

def align_and_score(expected_ipa, predicted_ipa):
    matcher = SequenceMatcher(None, expected_ipa, predicted_ipa)
    results = []
    total_dist = 0.0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        exp_slice = expected_ipa[i1:i2]
        pred_slice = predicted_ipa[j1:j2]

        # Handle matches and substitutions
        for e, p in zip(exp_slice, pred_slice):
            # Calculate raw PanPhon distance
            raw_dist = dst.feature_edit_distance(e, p)
            # Apply your specific scoring logic (Distance * 100)
            score = raw_dist * 100
            
            results.append({
                "expected": e,
                "predicted": p,
                "distance": raw_dist,
                "panphon_score": round(score, 2)
            })
            total_dist += raw_dist

    # Final overall word score
    max_features = 22 # PanPhon default feature count
    avg_score = 100 - (min(100, (total_dist * STRICTNESS_MULTIPLIER / max_features) * 100))
    
    return {
        "phoneme_breakdown": results,
        "overall_score": round(avg_score, 2)
    }