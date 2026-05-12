import numpy as np
import panphon.distance

# Initialize PanPhon Distance and Feature Table
dst = panphon.distance.Distance()
ft = panphon.FeatureTable()

def is_vowel(char):
    """Checks if a phoneme is a vowel using the 'syllabic' feature."""
    try:
        features = ft.word_to_vector_list(char, 0)[0]
        return features[0] == '+'
    except:
        return False

def get_clinical_distance(phoneme1, phoneme2):
    """Calculates distance for alignment with a Clinical Wall."""
    if is_vowel(phoneme1) != is_vowel(phoneme2):
        return 3.0  # Forces a Gap instead of swapping a vowel for a consonant
    return dst.feature_edit_distance(phoneme1, phoneme2)

def smart_align(target_ipa, detected_ipa):
    """Needleman-Wunsch Alignment optimized for SLP."""
    n, m = len(target_ipa), len(detected_ipa)
    gap_penalty = 0.8 
    
    score_matrix = np.zeros((n + 1, m + 1))
    for i in range(n + 1): score_matrix[i][0] = i * gap_penalty
    for j in range(m + 1): score_matrix[0][j] = j * gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub_cost = get_clinical_distance(target_ipa[i-1], detected_ipa[j-1])
            score_matrix[i][j] = min(
                score_matrix[i-1][j-1] + sub_cost,
                score_matrix[i-1][j] + gap_penalty,
                score_matrix[i][j-1] + gap_penalty
            )

    align_target, align_detected = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            sub_cost = get_clinical_distance(target_ipa[i-1], detected_ipa[j-1])
            if score_matrix[i][j] == score_matrix[i-1][j-1] + sub_cost:
                align_target.append(target_ipa[i-1])
                align_detected.append(detected_ipa[j-1])
                i -= 1; j -= 1
                continue
        if i > 0 and (j == 0 or score_matrix[i][j] == score_matrix[i-1][j] + gap_penalty):
            align_target.append(target_ipa[i-1])
            align_detected.append("-")
            i -= 1
        else:
            align_target.append("-")
            align_detected.append(detected_ipa[j-1])
            j -= 1
    return align_target[::-1], align_detected[::-1]

def align_and_score(expected_ipa, predicted_ipa):
    """
    Returns RAW feature distance and decimals.
    Tweak: High scores label as 'Correct' visually, but Substitutions 
    remain flagged for the Phonology Engine.
    """
    target_align, pred_align = smart_align(expected_ipa, predicted_ipa)
    results = []
    total_score = 0.0

    # THRESHOLD: If the score is above this, we visually label it "Correct"
    HIGH_SCORE_THRESHOLD = 90.0

    for e, p in zip(target_align, pred_align):
        # 1. Exact matches or 'g' variants
        is_identical = (e == p) or (e == 'g' and p == 'ɡ') or (e == 'ɡ' and p == 'g')

        if is_identical and e != "-":
            dist, score, insight = 0.0, 100.0, "Correct"
        elif p == "-" or e == "-":
            dist, score, insight = 1.0, 0.0, ("Omission" if p == "-" else "Insertion")
        else:
            # 2. Raw decimal math (e.g., 0.1875)
            dist = dst.feature_edit_distance(e, p)
            score = (1.0 - dist) * 100
            
            # Labeling logic for the JSON breakdown
            if score >= HIGH_SCORE_THRESHOLD:
                insight = "Correct"
            else:
                insight = "Substitution"

        results.append({
            "expected": e,
            "predicted": p,
            "score": round(float(score), 2),
            "dist": round(float(dist), 4),
            "insight": insight
        })
        total_score += score

    overall = round(total_score / len(results), 2) if results else 0
    return {"breakdown": results, "overall_score": overall}