# phoneme_processes/constants.py

STOPS = {'p', 'b', 't', 'd', 'k', 'g', 'ɡ'}
FRICATIVES = {'f', 'v', 'θ', 'ð', 's', 'z', 'ʃ', 'ʒ', 'h'}
AFFRICATES = {'tʃ', 'dʒ'}
LIQUIDS = {'l', 'r', 'ɹ'}
GLIDES = {'w', 'j'}
NASALS = {'m', 'n', 'ŋ'}

# Expanded vowels including Diphthongs and Rhotics
VOWELS = {
    'a', 'e', 'i', 'o', 'u', 'ə', 'ɔ', 'æ', 'ɑ', 'ʌ', 'ɛ', 'ɪ', 'ʊ',
    'aɪ', 'eɪ', 'oʊ', 'aʊ', 'ɔɪ', # Diphthongs
    'ɚ', 'ɝ'                      # Rhotic vowels
}

VELARS = {'k', 'g', 'ɡ', 'ŋ'}
PALATALS = {'ʃ', 'ʒ', 'tʃ', 'dʒ'}
ALVEOLARS = {'t', 'd', 's', 'z', 'n', 'l', 'ts', 'dz'}