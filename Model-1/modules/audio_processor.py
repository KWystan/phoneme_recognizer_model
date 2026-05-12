import librosa
import numpy as np

def clean_and_prepare_audio(audio_path, target_sr=16000):
    """
    Standardizes audio: Loads, resamples, trims silence, and normalizes volume.
    """
    # 1. Load & Resample (The AI strictly needs 16kHz)
    y, sr = librosa.load(audio_path, sr=target_sr)

    # 2. Trim Silence (Removes the dead air at the start/end)
    # top_db=20 is a good default for kids' voices
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)

    # 3. Normalize (Ensures the volume isn't too quiet for the AI)
    # This scales the wave so the loudest point is 1.0
    y_normalized = librosa.util.normalize(y_trimmed)

    return y_normalized