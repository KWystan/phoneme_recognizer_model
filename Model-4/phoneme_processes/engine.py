import re
from .constants import *
from .syllable_logic import check_syllable_reduction

class PhonologicalEngine:
    def __init__(self):
        pass

    def _clean(self, phoneme):
        """Standardizes phonemes by removing artifacts and stress marks."""
        if not phoneme or phoneme == "-":
            return "-"
        return re.sub(r'[0-9\:\-\sˈˌ]', '', phoneme)

    def get_groups(self, phoneme):
        """Maps a phoneme to its manner and place of articulation."""
        groups = {"manner": None, "place": None}
        p = self._clean(phoneme)
        if p == "-": return groups

        if p in STOPS: groups["manner"] = "Stop"
        elif p in FRICATIVES: groups["manner"] = "Fricative"
        elif p in AFFRICATES: groups["manner"] = "Affricate"
        elif p in LIQUIDS: groups["manner"] = "Liquid"
        elif p in GLIDES: groups["manner"] = "Glide"
        elif p in VOWELS: groups["manner"] = "Vowel"

        if p in VELARS: groups["place"] = "Velar"
        elif p in PALATALS: groups["place"] = "Palatal"
        elif p in ALVEOLARS: groups["place"] = "Alveolar"
        return groups

    def analyze_diagnostics(self, alignment_breakdown):
        detected_processes = []
        if not alignment_breakdown:
            return detected_processes

        # Pre-clean the alignment data
        clean_align = [
            {'expected': self._clean(e['expected']), 'predicted': self._clean(e['predicted'])} 
            for e in alignment_breakdown
        ]

        # --- STEP 1: SYLLABLE ANALYSIS ---
        syll_procs, skip_indices = check_syllable_reduction(clean_align)
        detected_processes.extend(syll_procs)

        # --- STEP 2: PHONEME-LEVEL ANALYSIS ---
        total_len = len(clean_align)
        
        # Helper: Find the index of the last non-vowel target consonant
        last_consonant_idx = -1
        for i in range(total_len - 1, -1, -1):
            if self.get_groups(clean_align[i]['expected'])["manner"] not in ["Vowel", None]:
                last_consonant_idx = i
                break

        for idx, entry in enumerate(clean_align):
            if idx in skip_indices:
                continue

            t, p = entry['expected'], entry['predicted']
            t_grp = self.get_groups(t)
            
            # Smart Positioning
            is_initial = (idx == 0)
            is_final = (idx == last_consonant_idx)
            pos = "Initial" if is_initial else "Final" if is_final else "Medial"

            if t == p or (t == "-" and p == "-"):
                continue

            # --- A. CLUSTER REDUCTION ---
            # Logic: If current target is a consonant and (prev or next) is a consonant, and one is deleted
            if t != "-" and p == "-" and t_grp["manner"] not in ["Vowel", None]:
                has_neighbor_consonant = False
                if idx > 0 and self.get_groups(clean_align[idx-1]['expected'])["manner"] not in ["Vowel", None]:
                    has_neighbor_consonant = True
                if idx < total_len - 1 and self.get_groups(clean_align[idx+1]['expected'])["manner"] not in ["Vowel", None]:
                    has_neighbor_consonant = True
                
                if has_neighbor_consonant:
                    detected_processes.append({
                        "process": "Cluster Reduction", 
                        "position": "Initial" if idx < total_len/2 else "Final", 
                        "detail": f"Reduced cluster at {t}"
                    })
                    skip_indices.add(idx)
                    continue

            # --- B. CONSONANT DELETIONS ---
            if t != "-" and p == "-" and t_grp["manner"] != "Vowel":
                # Ensure it's not a cluster (already handled)
                if idx not in skip_indices:
                    if is_initial:
                        detected_processes.append({"process": "Initial Consonant Deletion", "position": "Initial", "detail": f"{t}->-"})
                    elif is_final:
                        detected_processes.append({"process": "Final Consonant Deletion", "position": "Final", "detail": f"{t}->-"})
                    else:
                        detected_processes.append({"process": "Consonant Deletion", "position": "Medial", "detail": f"{t}->-"})
                continue

            # --- C. SUBSTITUTIONS ---
            if t == "-" or p == "-": continue 
            p_grp = self.get_groups(p)

            # 1. Backing / Fronting
            if t_grp["place"] == "Alveolar" and p_grp["place"] == "Velar":
                detected_processes.append({"process": "Backing", "position": pos, "detail": f"{t}->{p}"})
            elif t_grp["place"] == "Velar" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Fronting", "position": pos, "detail": f"{t}->{p}"})
            
            # 2. Stopping
            elif t_grp["manner"] in ["Fricative", "Affricate"] and p_grp["manner"] == "Stop":
                detected_processes.append({"process": "Stopping", "position": pos, "detail": f"{t}->{p}"})
            
            # 3. Liquidization / Gliding
            elif t_grp["manner"] in ["Glide", "Fricative"] and p_grp["manner"] == "Liquid":
                detected_processes.append({"process": "Liquidization", "position": pos, "detail": f"{t}->{p}"})
            elif t_grp["manner"] == "Liquid" and p_grp["manner"] == "Glide":
                detected_processes.append({"process": "Gliding", "position": pos, "detail": f"{t}->{p}"})

        # --- STEP 3: DEDUPLICATION ---
        unique_results = []
        seen = set()
        for d in detected_processes:
            t_key = tuple(sorted(d.items()))
            if t_key not in seen:
                unique_results.append(d)
                seen.add(t_key)
        
        return unique_results

engine = PhonologicalEngine()