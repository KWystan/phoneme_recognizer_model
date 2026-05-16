import numpy as np
import librosa
import pyloudnorm as pyln

def load_audio(source, sr: int = 16000):
    audio, loaded_sr = librosa.load(source, sr=sr, mono=True)
    return audio.astype(np.float32), loaded_sr

def loudness_normalize(audio: np.ndarray, sr: int, target_lufs: float = -20.0) -> np.ndarray:
    try:
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(audio)
        return pyln.normalize.loudness(audio, loudness, target_lufs).astype(np.float32)
    except:
        return peak_normalize(audio)

def peak_normalize(audio: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    peak = np.max(np.abs(audio))
    return (audio / peak * target_peak).astype(np.float32) if peak > 0 else audio