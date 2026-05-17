from core.audio_utils import load_audio, loudness_normalize, peak_normalize
from modules.preprocess import apply_deep_denoise, apply_silero_vad
from core.quality import compute_audio_stats, evaluate_audio_quality

def clean_and_prepare_audio(audio_source, target_sr=16000):
    # 1. Load raw audio
    audio, sr = load_audio(audio_source, sr=target_sr)
    
    # 2. Extract Speech (VAD)
    # We do this first so the denoiser only processes actual speech
    audio = apply_silero_vad(audio, sr=sr)
    
    # 3. Apply Deep Learning Denoising
    audio = apply_deep_denoise(audio)
    
    # 4. Final Volume Adjustment
    audio = loudness_normalize(audio, sr=sr)
    audio_final = peak_normalize(audio)
    
    # 5. Get metrics
    stats = compute_audio_stats(audio_final, target_sr)
    quality = evaluate_audio_quality(stats)

    return audio_final, quality, stats