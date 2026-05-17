# phoneme_processes/engine.py
from .utils import clean_phoneme
from .syllable_logic import check_weak_syllable_deletion
from .phoneme_logic import check_phoneme_processes

class PhonologicalEngine:
    def __init__(self):
        pass

    def analyze_diagnostics(self, alignment_breakdown):
        detected_processes = []
        if not alignment_breakdown:
            return detected_processes

        syll_procs, skip_indices = check_weak_syllable_deletion(alignment_breakdown)
        detected_processes.extend(syll_procs)

        clean_align = [{'expected': clean_phoneme(e['expected']), 'predicted': clean_phoneme(e['predicted'])} for e in alignment_breakdown]

        phoneme_procs = check_phoneme_processes(clean_align, skip_indices)
        detected_processes.extend(phoneme_procs)

        # Deduplication
        unique_results = []
        seen = set()
        for d in detected_processes:
            t_key = tuple(sorted(d.items()))
            if t_key not in seen:
                unique_results.append(d)
                seen.add(t_key)
        
        return unique_results

engine = PhonologicalEngine()