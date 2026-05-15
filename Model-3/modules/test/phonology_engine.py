# --- COPY YOUR CLASS HERE ---
class PhonologicalEngine:
    def __init__(self):
        # MANNER OF ARTICULATION
        self.STOPS = {'p', 'b', 't', 'd', 'k', 'g', 'ɡ'}
        self.FRICATIVES = {'f', 'v', 'θ', 'ð', 's', 'z', 'ʃ', 'ʒ', 'h'}
        self.AFFRICATES = {'tʃ', 'dʒ'}
        self.LIQUIDS = {'l', 'r', 'ɹ'}
        self.GLIDES = {'w', 'j'}
        self.VOWELS = {'a', 'e', 'i', 'o', 'u', 'ə', 'ɔ', 'ɛ', 'ɪ', 'ʊ'}

        # PLACE OF ARTICULATION
        self.VELARS = {'k', 'g', 'ɡ', 'ŋ'}
        self.PALATALS = {'ʃ', 'ʒ', 'tʃ', 'dʒ'}
        self.ALVEOLARS = {'t', 'd', 's', 'z', 'n', 'l', 'ts', 'dz'}

    def get_groups(self, phoneme):
        groups = {"manner": None, "place": None}
        if phoneme in self.STOPS: groups["manner"] = "Stop"
        elif phoneme in self.FRICATIVES: groups["manner"] = "Fricative"
        elif phoneme in self.AFFRICATES: groups["manner"] = "Affricate"
        elif phoneme in self.LIQUIDS: groups["manner"] = "Liquid"
        elif phoneme in self.GLIDES: groups["manner"] = "Glide"
        elif phoneme in self.VOWELS: groups["manner"] = "Vowel"

        if phoneme in self.VELARS: groups["place"] = "Velar"
        elif phoneme in self.PALATALS: groups["place"] = "Palatal"
        elif phoneme in self.ALVEOLARS: groups["place"] = "Alveolar"
        return groups

    def analyze_diagnostics(self, alignment_breakdown):
        detected_processes = []
        for entry in alignment_breakdown:
            target, spoken = entry['expected'], entry['predicted']
            if target == spoken or target == "-" or spoken == "-": continue

            t_grp, p_grp = self.get_groups(target), self.get_groups(spoken)

            if t_grp["place"] == "Alveolar" and p_grp["place"] == "Velar":
                detected_processes.append({"process": "Backing", "detail": f"{target}->{spoken}"})
            elif t_grp["place"] == "Velar" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Fronting", "detail": f"{target}->{spoken}"})
            elif t_grp["place"] == "Palatal" and p_grp["place"] == "Alveolar":
                detected_processes.append({"process": "Palatal Fronting", "detail": f"{target}->{spoken}"})
            elif t_grp["manner"] == "Liquid" and p_grp["manner"] == "Glide":
                detected_processes.append({"process": "Gliding", "detail": f"{target}->{spoken}"})
            elif t_grp["manner"] in ["Fricative", "Affricate"] and p_grp["manner"] == "Stop":
                detected_processes.append({"process": "Stopping", "detail": f"{target}->{spoken}"})
            elif t_grp["manner"] == "Stop" and p_grp["manner"] == "Fricative":
                detected_processes.append({"process": "Frication", "detail": f"{target}->{spoken}"})
            elif t_grp["manner"] == "Affricate" and p_grp["manner"] == "Fricative":
                detected_processes.append({"process": "Deaffrication", "detail": f"{target}->{spoken}"})
            elif t_grp["manner"] == "Liquid" and p_grp["manner"] == "Vowel":
                detected_processes.append({"process": "Vowelization", "detail": f"{target}->{spoken}"})

        return [dict(t) for t in {tuple(d.items()) for d in detected_processes}]

# --- TESTING PROGRAM ---

def run_test(label, expected_list, predicted_list):
    engine = PhonologicalEngine()
    
    # Simulate the alignment breakdown format
    breakdown = []
    for e, p in zip(expected_list, predicted_list):
        breakdown.append({"expected": e, "predicted": p})

    processes = engine.analyze_diagnostics(breakdown)
    
    print(f"--- TEST: {label} ---")
    print(f"Expected: {''.join(expected_list)}")
    print(f"Detected: {''.join(predicted_list)}")
    if processes:
        for proc in processes:
            print(f"✅ FOUND: {proc['process']} ({proc['detail']})")
    else:
        print("❌ No processes detected.")
    print("-" * 30)

if __name__ == "__main__":
    # YOU CAN EDIT THESE LISTS TO TEST ANYTHING
    # Just ensure the lengths of expected and predicted match
    
    # 1. Bunny Example (b -> v is Frication)
    run_test("Bunny/Frication", ['b', 'ə', 'n', 'i'], ['v', 'a', 'n', 'i'])
