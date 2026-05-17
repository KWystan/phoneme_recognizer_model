# phoneme_processes/utils.py
import re
from .constants import *

def clean_phoneme(phoneme):
    """Standardizes phonemes by removing artifacts and stress marks."""
    if not phoneme or phoneme == "-":
        return "-"
    # Removes length marks, half-length marks, stress, and colons
    cleaned = re.sub(r'[0-9\:\-\sˈˌ\u02d0\u02d1]', '', phoneme)
    if cleaned == "":
        return "-"
    return cleaned

def get_phoneme_groups(phoneme):
    """Maps a phoneme to its manner and place of articulation."""
    groups = {"manner": None, "place": None}
    p = clean_phoneme(phoneme)
    if p == "-": return groups

    # Manner
    if p in STOPS: groups["manner"] = "Stop"
    elif p in FRICATIVES: groups["manner"] = "Fricative"
    elif p in AFFRICATES: groups["manner"] = "Affricate"
    elif p in LIQUIDS: groups["manner"] = "Liquid"
    elif p in GLIDES: groups["manner"] = "Glide"
    elif p in VOWELS: groups["manner"] = "Vowel"
    elif p in NASALS: groups["manner"] = "Nasal"

    # Place
    if p in VELARS: groups["place"] = "Velar"
    elif p in PALATALS: groups["place"] = "Palatal"
    elif p in ALVEOLARS: groups["place"] = "Alveolar"

    return groups

def tokenize_ipa(ipa_string):
    """
    Cleans the IPA string and chunks it into logical phonemes 
    (handling diphthongs, affricates, and rhotics).
    """
    if not ipa_string:
        return []

    # 1. Clean artifacts
    cleaned = re.sub(r'[0-9\:\-\sˈˌ\u02d0\u02d1]', '', ipa_string)
    
    # 2. Standardize rhotics to match the AI output
    cleaned = cleaned.replace('ər', 'ɚ').replace('ɜr', 'ɝ')
    
    # 3. Tokenize pairs
    tokens = []
    i = 0
    while i < len(cleaned):
        if i + 1 < len(cleaned):
            pair = cleaned[i:i+2]
            if pair in ['aɪ', 'eɪ', 'oʊ', 'aʊ', 'ɔɪ', 'tʃ', 'dʒ']:
                tokens.append(pair)
                i += 2
                continue
        tokens.append(cleaned[i])
        i += 1
        
    return tokens