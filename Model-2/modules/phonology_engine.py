class PhonologicalEngine:
    def __init__(self):
        # Expanded ASHA Map
        self.asha_map = {
            # BACKING
            ('t', 'k'): "Backing", ('d', 'g'): "Backing", ('n', 'ŋ'): "Backing",
            ('s', 'k'): "Backing", ('z', 'g'): "Backing", ('ts', 'k'): "Backing",
            ('t', 'h'): "Backing", ('d', 'h'): "Backing",

            # FRONTING
            ('k', 't'): "Fronting", ('g', 'd'): "Fronting", ('ŋ', 'n'): "Fronting",
            ('ʃ', 's'): "Fronting", ('ʒ', 'z'): "Fronting", ('tʃ', 'ts'): "Fronting",
            ('dʒ', 'dz'): "Fronting", ('k', 'p'): "Fronting",

            # STOPPING
            ('f', 'p'): "Stopping", ('v', 'b'): "Stopping", ('s', 't'): "Stopping",
            ('z', 'd'): "Stopping", ('ʃ', 't'): "Stopping", ('ʒ', 'd'): "Stopping",
            ('θ', 't'): "Stopping", ('ð', 'd'): "Stopping", ('tʃ', 't'): "Stopping",
            ('dʒ', 'd'): "Stopping", ('s', 'p'): "Stopping", ('f', 't'): "Stopping",

            # GLIDING
            ('r', 'w'): "Gliding", ('l', 'w'): "Gliding", ('l', 'j'): "Gliding",
            ('ɹ', 'w'): "Gliding", ('r', 'j'): "Gliding",

            # FRICATION / LABIALIZATION
            ('b', 'v'): "Frication/Labialization", ('p', 'f'): "Frication",
            
            # DEAFFRICATION
            ('tʃ', 'ʃ'): "Deaffrication", ('dʒ', 'ʒ'): "Deaffrication",

            # VOWELIZATION
            ('l', 'o'): "Vowelization", ('l', 'u'): "Vowelization", 
            ('r', 'o'): "Vowelization", ('er', 'ə'): "Vowelization",
            
            # DENASALIZATION
            ('m', 'b'): "Denasalization", ('n', 'd'): "Denasalization", 
        }

    def analyze_diagnostics(self, alignment_breakdown):
        detected_processes = []
        if not alignment_breakdown:
            return detected_processes
            
        # 1. Syllable Structure Logic
        if alignment_breakdown[0]['predicted'] == "-":
            detected_processes.append({"process": "Initial Consonant Deletion"})
        
        # Check for Final Consonant Deletion (last intended phoneme)
        last_item = next((i for i in reversed(alignment_breakdown) if i['expected'] != "-"), None)
        if last_item and last_item['predicted'] == "-":
            detected_processes.append({"process": "Final Consonant Deletion"})

        # 2. Substitution Logic (Checks every swap regardless of score)
        for entry in alignment_breakdown:
            target = entry['expected']
            spoken = entry['predicted']
            
            # If the characters are different, check the clinical map
            if target != spoken and (target, spoken) in self.asha_map:
                detected_processes.append({
                    "process": self.asha_map[(target, spoken)],
                    "detail": f"{target} -> {spoken}"
                })
        
        # Remove duplicates
        return [dict(t) for t in {tuple(d.items()) for d in detected_processes}]

# CRITICAL: Export engine for main application
engine = PhonologicalEngine()