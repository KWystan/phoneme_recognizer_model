# phoneme_processes/syllable_logic.py
from .utils import clean_phoneme, get_phoneme_groups

def check_weak_syllable_deletion(raw_alignment):
    syll_procs = []
    skip_indices = set()
    
    buckets = []
    current_bucket = []
    for i, entry in enumerate(raw_alignment):
        current_bucket.append(i)
        clean_t = clean_phoneme(entry['expected'])
        t_manner = get_phoneme_groups(clean_t)["manner"]
        
        if t_manner == "Vowel":
            buckets.append(current_bucket)
            current_bucket = []
            
    if current_bucket:
        if buckets: buckets[-1].extend(current_bucket)
        else: buckets.append(current_bucket)

    for i, bucket_indices in enumerate(buckets):
        is_deleted = True
        syllable_parts = []
        
        for idx in bucket_indices:
            entry = raw_alignment[idx]
            clean_t = clean_phoneme(entry['expected'])
            
            if clean_t != "-": 
                syllable_parts.append(clean_t)
                if entry['predicted'] != "-":
                    is_deleted = False

        if is_deleted and syllable_parts:
            pos = "Initial" if i == 0 else "Final" if i == len(buckets) - 1 else "Medial"
            deleted_syllable = "".join(syllable_parts)
            syll_procs.append({
                "process": "Weak Syllable Deletion",
                "position": pos,
                "detail": f"Syllable '{deleted_syllable}' deleted"
            })
            for idx in bucket_indices:
                skip_indices.add(idx)
                
    return syll_procs, skip_indices