import re
# Assuming constants are defined in your project: STOPS, FRICATIVES, etc.
from .constants import *

class PhonologicalEngine:
    def __init__(self):
        pass

    def _clean(self, phoneme):
            """Standardizes phonemes by removing artifacts and stress marks."""
            if not phoneme or phoneme == "-":
                return "-"
                
            # Handles length marks and stress marks often found in AI IPA output
            cleaned = re.sub(r'[0-9\:\-\sˈˌ\u02d0]', '', phoneme)
            
            # NEW: If stripping the marks leaves us with nothing, it counts as an omission!
            if cleaned == "":
                return "-"
                
            return cleaned

    def get_groups(self, phoneme):
            """Maps a phoneme to its manner and place of articulation."""
            groups = {"manner": None, "place": None}
            p = self._clean(phoneme)
            if p == "-": return groups

            # --- Manner ---
            if p in STOPS: groups["manner"] = "Stop"
            elif p in FRICATIVES: groups["manner"] = "Fricative"
            elif p in AFFRICATES: groups["manner"] = "Affricate"
            elif p in LIQUIDS: groups["manner"] = "Liquid"
            elif p in GLIDES: groups["manner"] = "Glide"
            elif p in VOWELS: groups["manner"] = "Vowel"
            elif p in NASALS: groups["manner"] = "Nasal" # NEW: Added this line!

            # --- Place ---
            if p in VELARS: groups["place"] = "Velar"
            elif p in PALATALS: groups["place"] = "Palatal"
            elif p in ALVEOLARS: groups["place"] = "Alveolar"
            
            # Note: If you added BILABIALS, LABIODENTALS, etc. to your constants earlier, 
            # make sure to add their elif statements here too!

            return groups

    def _check_weak_syllable_deletion(self, raw_alignment):
            """
            Groups alignment into syllable buckets based on target vowels.
            If an entire syllable is omitted, it flags Syllable Deletion and 
            skips those indices to prevent redundant consonant deletion flags.
            """
            syll_procs = []
            skip_indices = set()
            
            # 1. Group indices into syllable buckets based on vowel nuclei
            buckets = []
            current_bucket = []
            for i, entry in enumerate(raw_alignment):
                current_bucket.append(i)
                clean_t = self._clean(entry['expected'])
                t_manner = self.get_groups(clean_t)["manner"]
                
                # Whenever we hit a vowel, we close the current bucket
                if t_manner == "Vowel":
                    buckets.append(current_bucket)
                    current_bucket = []
                    
            # Catch any remaining consonants at the end (coda) and add them to the last bucket
            if current_bucket:
                if buckets:
                    buckets[-1].extend(current_bucket)
                else:
                    buckets.append(current_bucket)

            # 2. Check each bucket for total omission
            for i, bucket_indices in enumerate(buckets):
                is_deleted = True
                syllable_parts = []
                
                for idx in bucket_indices:
                    entry = raw_alignment[idx]
                    clean_t = self._clean(entry['expected'])
                    
                    if clean_t != "-": # Ignore alignment insertions
                        syllable_parts.append(clean_t)
                        # If any expected sound in this syllable was actually spoken, it's not a full deletion
                        if entry['predicted'] != "-":
                            is_deleted = False

                # If the bucket is completely empty and actually had expected sounds
                if is_deleted and syllable_parts:
                    # Determine syllable position based on the bucket index
                    if i == 0: pos = "Initial"
                    elif i == len(buckets) - 1: pos = "Final"
                    else: pos = "Medial"
                    
                    deleted_syllable = "".join(syllable_parts)
                    
                    syll_procs.append({
                        "process": "Weak Syllable Deletion",
                        "position": pos,
                        "detail": f"Syllable '{deleted_syllable}' deleted"
                    })
                    
                    # Mark ALL these indices to prevent redundant phoneme-level flags (like Initial Consonant Deletion)
                    for idx in bucket_indices:
                        skip_indices.add(idx)
                        
            return syll_procs, skip_indices

    def analyze_diagnostics(self, alignment_breakdown):
        detected_processes = []
        if not alignment_breakdown:
            return detected_processes

        # --- STEP 1: SYLLABLE ANALYSIS (Uses RAW data to keep stress marks) ---
        syll_procs, skip_indices = self._check_weak_syllable_deletion(alignment_breakdown)
        detected_processes.extend(syll_procs)

        # Pre-clean the alignment data for the rest of the consonant/phoneme checks
        clean_align = [
            {'expected': self._clean(e['expected']), 'predicted': self._clean(e['predicted'])} 
            for e in alignment_breakdown
        ]

        # --- STEP 2: PHONEME-LEVEL ANALYSIS ---
        total_len = len(clean_align)
        
        # Helper: Find true FIRST expected consonant (ignores initial insertions)
        first_consonant_idx = -1
        for i in range(total_len):
            t_val = clean_align[i]['expected']
            if t_val != "-" and self.get_groups(t_val)["manner"] not in ["Vowel", None]:
                first_consonant_idx = i
                break

        # Helper: Find true LAST expected consonant (ignores final insertions)
        last_consonant_idx = -1
        for i in range(total_len - 1, -1, -1):
            t_val = clean_align[i]['expected']
            if t_val != "-" and self.get_groups(t_val)["manner"] not in ["Vowel", None]:
                last_consonant_idx = i
                break

        for idx, entry in enumerate(clean_align):
            if idx in skip_indices:
                continue

            t, p = entry['expected'], entry['predicted']
            t_grp = self.get_groups(t)
            p_grp = self.get_groups(p) # Added this so substitutions don't crash when comparing p_grp
            
            # Smart Positioning: Resilient to insertions pushing the index around
            is_initial = (idx <= first_consonant_idx) if first_consonant_idx != -1 else (idx == 0)
            is_final = (idx == last_consonant_idx)
            pos = "Initial" if is_initial else "Final" if is_final else "Medial"

            if t == p or (t == "-" and p == "-"):
                continue

            # --- A. CLUSTER REDUCTION ---
            if t != "-" and p == "-" and t_grp["manner"] not in ["Vowel", None]:
                has_neighbor_consonant = False
                
                # Look backwards for the nearest true expected phoneme
                for prev_idx in range(idx - 1, -1, -1):
                    prev_target = clean_align[prev_idx]['expected']
                    if prev_target != "-":
                        if self.get_groups(prev_target)["manner"] not in ["Vowel", None]:
                            has_neighbor_consonant = True
                        break 
                
                # Look forwards for the nearest true expected phoneme
                if not has_neighbor_consonant: 
                    for next_idx in range(idx + 1, total_len):
                        next_target = clean_align[next_idx]['expected']
                        if next_target != "-":
                            if self.get_groups(next_target)["manner"] not in ["Vowel", None]:
                                has_neighbor_consonant = True
                            break

                if has_neighbor_consonant:
                    detected_processes.append({
                        "process": "Cluster Reduction", 
                        "position": "Initial" if idx < total_len/2 else "Final", 
                        "detail": f"Reduced cluster at {t}"
                    })
                    skip_indices.add(idx)
                    continue

            # --- B. CONSONANT DELETIONS ---
            if t != "-" and p == "-" and t_grp["manner"] not in ["Vowel", None]:
                if idx not in skip_indices:
                    if is_initial:
                        detected_processes.append({"process": "Initial Consonant Deletion", "position": "Initial", "detail": f"{t}->-"})
                    elif is_final:
                        detected_processes.append({"process": "Final Consonant Deletion", "position": "Final", "detail": f"{t}->-"})
                continue

            # --- C. SUBSTITUTIONS (STRICT LIST) ---
            if t == "-" or p == "-": continue 

            # 1. BACKING: Alveolar -> Velar
            if t_grp["place"] == "Alveolar" and p_grp["place"] == "Velar":
                detected_processes.append({"process": "Backing", "position": pos, "detail": f"{t}->{p}"})

            # 2. FRONTING: Velar -> Alveolar
            elif t_grp["place"] == "Velar" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Fronting", "position": pos, "detail": f"{t}->{p}"})

            # 3. PALATAL FRONTING: Palatal -> Alveolar
            elif t_grp["place"] == "Palatal" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Palatal Fronting", "position": pos, "detail": f"{t}->{p}"})

            # 4. GLIDING: Liquid <-> Glide
            elif (t_grp["manner"] == "Liquid" and p_grp["manner"] == "Glide"):
                detected_processes.append({"process": "Gliding", "position": pos, "detail": f"{t}->{p}"})

            # 5. STOPPING: Fricative/Affricate -> Stop
            elif t_grp["manner"] in ["Fricative", "Affricate"] and p_grp["manner"] == "Stop":
                detected_processes.append({"process": "Stopping", "position": pos, "detail": f"{t}->{p}"})

            # 6. DEAFFRICATION: Affricate -> Fricative
            elif t_grp["manner"] == "Affricate" and p_grp["manner"] == "Fricative":
                detected_processes.append({"process": "Deaffrication", "position": pos, "detail": f"{t}->{p}"})

            # 7. VOWELIZATION: Liquid -> Vowel (This is what handles your Vowelization requirement!)
            elif t_grp["manner"] == "Liquid" and p_grp["manner"] == "Vowel":
                detected_processes.append({"process": "Vowelization", "position": pos, "detail": f"{t}->{p}"})

            # 8. FRICATION: Stop -> Fricative
            elif t_grp["manner"] == "Stop" and p_grp["manner"] == "Fricative":
                detected_processes.append({"process": "Frication", "position": pos, "detail": f"{t}->{p}"})

            # 9. LIQUIDIZATION: Glide/Fricative -> Liquid
            elif t_grp["manner"] in ["Glide", "Fricative"] and p_grp["manner"] == "Liquid":
                detected_processes.append({"process": "Liquidization", "position": pos, "detail": f"{t}->{p}"})

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