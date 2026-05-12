import numpy as np
import webrtcvad
import noisereduce as nr

from core.audio_utils import float_to_pcm16, pcm16_to_float

def apply_vad(audio: np.ndarray, sr: int = 16000, mode: int = 2,
              frame_ms: int = 30, pad_ms: int = 150) -> np.ndarray:
    if len(audio) == 0:
        return audio

    if frame_ms not in (10, 20, 30):
        raise ValueError("frame_ms must be 10, 20, or 30")

    vad = webrtcvad.Vad(mode)
    frame_len = int(sr * frame_ms / 1000)
    pcm = float_to_pcm16(audio)

    bytes_per_frame = frame_len * 2
    frames = [
        pcm[i:i + bytes_per_frame]
        for i in range(0, len(pcm) - bytes_per_frame + 1, bytes_per_frame)
    ]

    if not frames:
        return np.array([], dtype=np.float32)

    voiced_flags = [vad.is_speech(frame, sr) for frame in frames]
    voiced_indices = [i for i, flag in enumerate(voiced_flags) if flag]

    if not voiced_indices:
        return np.array([], dtype=np.float32)

    pad_frames = int(pad_ms / frame_ms)
    start_idx = max(0, voiced_indices[0] - pad_frames)
    end_idx = min(len(frames), voiced_indices[-1] + 1 + pad_frames)

    voiced_pcm = b"".join(frames[start_idx:end_idx])
    voiced_audio = pcm16_to_float(voiced_pcm)
    return voiced_audio.astype(np.float32)

def apply_denoise(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    if len(audio) == 0:
        return audio
    cleaned = nr.reduce_noise(y=audio, sr=sr)
    return cleaned.astype(np.float32)