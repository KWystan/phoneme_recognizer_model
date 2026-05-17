# phoneme_processes/phoneme_logic.py
from .utils import get_phoneme_groups

def check_phoneme_processes(clean_align, skip_indices):
    detected_processes = []
    total_len = len(clean_align)
    
    first_consonant_idx, last_consonant_idx = -1, -1
    for i in range(total_len):
        t_val = clean_align[i]['expected']
        if t_val != "-" and get_phoneme_groups(t_val)["manner"] not in ["Vowel", None]:
            first_consonant_idx = i
            break

    for i in range(total_len - 1, -1, -1):
        t_val = clean_align[i]['expected']
        if t_val != "-" and get_phoneme_groups(t_val)["manner"] not in ["Vowel", None]:
            last_consonant_idx = i
            break

    for idx, entry in enumerate(clean_align):
        if idx in skip_indices: continue

        t, p = entry['expected'], entry['predicted']
        t_grp, p_grp = get_phoneme_groups(t), get_phoneme_groups(p)
        
        is_initial = (idx <= first_consonant_idx) if first_consonant_idx != -1 else (idx == 0)
        is_final = (idx == last_consonant_idx)
        pos = "Initial" if is_initial else "Final" if is_final else "Medial"

        if t == p or (t == "-" and p == "-"): continue

        # Cluster Reduction
        if t != "-" and p == "-" and t_grp["manner"] not in ["Vowel", None]:
            has_neighbor = False
            for prev_idx in range(idx - 1, -1, -1):
                prev_t = clean_align[prev_idx]['expected']
                if prev_t != "-" and get_phoneme_groups(prev_t)["manner"] not in ["Vowel", None]:
                    has_neighbor = True; break 
            if not has_neighbor: 
                for next_idx in range(idx + 1, total_len):
                    next_t = clean_align[next_idx]['expected']
                    if next_t != "-" and get_phoneme_groups(next_t)["manner"] not in ["Vowel", None]:
                        has_neighbor = True; break
            if has_neighbor:
                detected_processes.append({"process": "Cluster Reduction", "position": "Initial" if idx < total_len/2 else "Final", "detail": f"Reduced cluster at {t}"})
                skip_indices.add(idx)
                continue

            # Consonant Deletions
            if idx not in skip_indices:
                if is_initial: detected_processes.append({"process": "Initial Consonant Deletion", "position": "Initial", "detail": f"{t}->-"})
                elif is_final: detected_processes.append({"process": "Final Consonant Deletion", "position": "Final", "detail": f"{t}->-"})
            continue

        # Substitutions
        if t == "-" or p == "-": continue 
        if t_grp["place"] == "Alveolar" and p_grp["place"] == "Velar": detected_processes.append({"process": "Backing", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["place"] == "Velar" and p_grp["place"] == "Alveolar": detected_processes.append({"process": "Fronting", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["place"] == "Palatal" and p_grp["place"] == "Alveolar": detected_processes.append({"process": "Palatal Fronting", "position": pos, "detail": f"{t}->{p}"})
        elif (t_grp["manner"] == "Liquid" and p_grp["manner"] == "Glide"): detected_processes.append({"process": "Gliding", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["manner"] in ["Fricative", "Affricate"] and p_grp["manner"] == "Stop": detected_processes.append({"process": "Stopping", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["manner"] == "Affricate" and p_grp["manner"] == "Fricative": detected_processes.append({"process": "Deaffrication", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["manner"] == "Liquid" and p_grp["manner"] == "Vowel": detected_processes.append({"process": "Vowelization", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["manner"] == "Stop" and p_grp["manner"] == "Fricative": detected_processes.append({"process": "Frication", "position": pos, "detail": f"{t}->{p}"})
        elif t_grp["manner"] in ["Glide", "Fricative"] and p_grp["manner"] == "Liquid": detected_processes.append({"process": "Liquidization", "position": pos, "detail": f"{t}->{p}"})

    return detected_processes