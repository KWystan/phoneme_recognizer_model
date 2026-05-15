class PhonologicalEngine:
    def __init__(self):
        # --- SOUND GROUPS (Manner) ---
        self.STOPS = {'p', 'b', 't', 'd', 'k', 'g', 'ɡ'}
        self.FRICATIVES = {'f', 'v', 'θ', 'ð', 's', 'z', 'ʃ', 'ʒ', 'h'}
        self.AFFRICATES = {'tʃ', 'dʒ'}
        self.LIQUIDS = {'l', 'r', 'ɹ'}
        self.GLIDES = {'w', 'j'}
        self.VOWELS = {'a', 'e', 'i', 'o', 'u', 'ə', 'ɔ', 'ɛ', 'ɪ', 'ʊ'}

        # --- SOUND GROUPS (Place) ---
        self.VELARS = {'k', 'g', 'ɡ', 'ŋ'}
        self.PALATALS = {'ʃ', 'ʒ', 'tʃ', 'dʒ'}
        self.ALVEOLARS = {'t', 'd', 's', 'z', 'n', 'l', 'ts', 'dz'}

    def get_groups(self, phoneme):
        """Maps a phoneme to its linguistic categories."""
        groups = {"manner": None, "place": None}

        # Determine Manner
        if phoneme in self.STOPS: groups["manner"] = "Stop"
        elif phoneme in self.FRICATIVES: groups["manner"] = "Fricative"
        elif phoneme in self.AFFRICATES: groups["manner"] = "Affricate"
        elif phoneme in self.LIQUIDS: groups["manner"] = "Liquid"
        elif phoneme in self.GLIDES: groups["manner"] = "Glide"
        elif phoneme in self.VOWELS: groups["manner"] = "Vowel"

        # Determine Place
        if phoneme in self.VELARS: groups["place"] = "Velar"
        elif phoneme in self.PALATALS: groups["place"] = "Palatal"
        elif phoneme in self.ALVEOLARS: groups["place"] = "Alveolar"

        return groups

    def analyze_diagnostics(self, alignment_breakdown):
        """
        Scans the breakdown for categorical shifts. 
        Ignores 'insight' or 'score'—only looks at the sounds themselves.
        Now detects positions (Initial, Medial, Final) and Deletions.
        """
        detected_processes = []
        if not alignment_breakdown:
            return detected_processes

        total_len = len(alignment_breakdown)

        for idx, entry in enumerate(alignment_breakdown):
            target = entry['expected']
            spoken = entry['predicted']

            # --- DETERMINE POSITION ---
            if idx == 0:
                pos = "Initial"
            elif idx == total_len - 1:
                pos = "Final"
            else:
                pos = "Medial"

            # --- DETECT CONSONANT DELETIONS (Omissions) ---
            if target != "-" and spoken == "-":
                t_grp = self.get_groups(target)
                # Only evaluate consonant deletions
                if t_grp["manner"] != "Vowel":
                    if pos == "Initial":
                        detected_processes.append({"process": "Initial Consonant Deletion", "position": pos, "detail": f"{target}->-"})
                    elif pos == "Final":
                        detected_processes.append({"process": "Final Consonant Deletion", "position": pos, "detail": f"{target}->-"})
                continue

            # Only evaluate actual substitutions (ignore same sounds or gaps/insertions)
            if target == spoken or target == "-" or spoken == "-":
                continue

            t_grp = self.get_groups(target)
            p_grp = self.get_groups(spoken)

            # --- STRICT PROCESS DETECTION ---
            
            # 1. BACKING: Alveolar -> Velar
            if t_grp["place"] == "Alveolar" and p_grp["place"] == "Velar":
                detected_processes.append({"process": "Backing", "position": pos, "detail": f"{target}->{spoken}"})

            # 2. FRONTING: Velar -> Alveolar
            elif t_grp["place"] == "Velar" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Fronting", "position": pos, "detail": f"{target}->{spoken}"})

            # 3. PALATAL FRONTING: Palatal -> Alveolar
            elif t_grp["place"] == "Palatal" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Palatal Fronting", "position": pos, "detail": f"{target}->{spoken}"})

            # 4. GLIDING: Liquid <-> Glide (Bidirectional per your ASHA list)
            elif (t_grp["manner"] == "Liquid" and p_grp["manner"] == "Glide") or \
                 (t_grp["manner"] == "Glide" and p_grp["manner"] == "Liquid"):
                detected_processes.append({"process": "Gliding", "position": pos, "detail": f"{target}->{spoken}"})

            # 5. STOPPING: Fricative/Affricate -> Stop
            elif t_grp["manner"] in ["Fricative", "Affricate"] and p_grp["manner"] == "Stop":
                detected_processes.append({"process": "Stopping", "position": pos, "detail": f"{target}->{spoken}"})

            # 6. DEAFFRICATION: Affricate -> Fricative
            elif t_grp["manner"] == "Affricate" and p_grp["manner"] == "Fricative":
                detected_processes.append({"process": "Deaffrication", "position": pos, "detail": f"{target}->{spoken}"})

            # 7. VOWELIZATION: Liquid -> Vowel
            elif t_grp["manner"] == "Liquid" and p_grp["manner"] == "Vowel":
                detected_processes.append({"process": "Vowelization", "position": pos, "detail": f"{target}->{spoken}"})

            # 8. FRICATION: Stop -> Fricative (e.g., b -> v)
            elif t_grp["manner"] == "Stop" and p_grp["manner"] == "Fricative":
                detected_processes.append({"process": "Frication", "position": pos, "detail": f"{target}->{spoken}"})

            # 9. LIQUIDIZATION (Atypical): Glide/Fricative -> Liquid
            # Example: Wig -> Rig (/w/->/r/), Muffin -> Murrin (/f/->/r/)
            if t_grp["manner"] in ["Glide", "Fricative"] and p_grp["manner"] == "Liquid":
                detected_processes.append({"process": "Liquidization", "position": pos, "detail": f"{target}->{spoken}"})

        # Remove duplicates
        return [dict(t) for t in {tuple(d.items()) for d in detected_processes}]

engine = PhonologicalEngine()