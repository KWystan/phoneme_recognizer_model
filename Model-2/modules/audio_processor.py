import librosa
import numpy as np

from core.audio_utils import load_audio, peak_normalize, trim_leading_trailing_silence
from modules.preprocess import apply_vad, apply_denoise  # Changed from 'preprocess' to 'modules.preprocess'

from core.quality import compute_audio_stats, evaluate_audio_quality

def clean_and_prepare_audio(audio_source, target_sr=16000):
    audio, sr = load_audio(audio_source, sr=target_sr)
    audio = trim_leading_trailing_silence(audio, top_db=28)
    audio = apply_vad(audio, sr=sr, mode=2, frame_ms=30, pad_ms=150)
    audio = apply_denoise(audio, sr=sr)
    audio_final = peak_normalize(audio, target_peak=0.95) # Save to variable
    
    # Calculate the stats and quality BEFORE returning
    from core.quality import compute_audio_stats, evaluate_audio_quality
    stats = compute_audio_stats(audio_final, target_sr)
    quality = evaluate_audio_quality(stats)

    # RETURN ALL THREE
    return audio_final, quality, stats