import numpy as np
import librosa

INT16_MAX = np.iinfo(np.int16).max

def load_audio(source, sr: int = 16000, mono: bool = True):
    audio, loaded_sr = librosa.load(source, sr=sr, mono=mono)
    return audio.astype(np.float32), loaded_sr

def peak_normalize(audio: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    if len(audio) == 0:
        return audio
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    return ((audio / peak) * target_peak).astype(np.float32)

def trim_leading_trailing_silence(audio: np.ndarray, top_db: int = 30):
    if len(audio) == 0:
        return audio
    trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
    return trimmed.astype(np.float32)

def float_to_pcm16(audio: np.ndarray) -> bytes:
    clipped = np.clip(audio, -1.0, 1.0)
    pcm16 = np.round(clipped * INT16_MAX).astype(np.int16)
    return pcm16.tobytes()

def pcm16_to_float(pcm_bytes: bytes) -> np.ndarray:
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    return (audio / INT16_MAX).astype(np.float32)