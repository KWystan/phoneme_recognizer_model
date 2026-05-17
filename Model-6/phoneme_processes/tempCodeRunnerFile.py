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