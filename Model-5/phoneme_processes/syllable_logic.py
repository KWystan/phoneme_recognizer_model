# phoneme_processes/syllable_logic.py
from .constants import VOWELS

def check_syllable_reduction(alignment):
    """
    Groups alignment into syllables based on target vowels.
    Returns: (list of processes, set of affected_indices)
    """
    syllable_processes = []
    affected_indices = set()
    
    # 1. Group indices into syllable buckets based on vowel nuclei
    buckets = []
    current_bucket = []
    for i, entry in enumerate(alignment):
        current_bucket.append(i)
        if entry['expected'] in VOWELS:
            buckets.append(current_bucket)
            current_bucket = []
            
    # Catch any remaining consonants at the end (coda)
    if current_bucket:
        if buckets:
            buckets[-1].extend(current_bucket)
        else:
            buckets.append(current_bucket)

    # 2. Check each bucket for total omission
    for i, bucket_indices in enumerate(buckets):
        if all(alignment[idx]['predicted'] == '-' for idx in bucket_indices):
            # Determine syllable position
            if i == 0: pos = "Initial"
            elif i == len(buckets) - 1: pos = "Final"
            else: pos = "Medial"
            
            syllable_processes.append({
                "process": "Weak Syllable Deletion",
                "position": pos,
                "detail": f"Syllable {i+1} omitted"
            })
            # Mark these indices to prevent redundant phoneme-level flags
            for idx in bucket_indices:
                affected_indices.add(idx)
                
    return syllable_processes, affected_indices