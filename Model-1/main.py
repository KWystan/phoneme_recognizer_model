from modules.audio_processor import clean_and_prepare_audio
from model.phoneme_recognizer import recognizer

def process_voice_request(file_path):
    # Step A: Clean the audio (Signal Processing)
    clean_audio = clean_and_prepare_audio(file_path)
    
    # Step B: Get Phonemes (AI Inference)
    spoken_phonemes = recognizer.get_phonemes(clean_audio)
    
    return spoken_phonemes