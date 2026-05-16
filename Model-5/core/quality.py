import numpy as np


def _clean_numeric_audio(audio):
    audio = np.asarray(audio, dtype=np.float32)
    if audio.size == 0:
        return audio
    return np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)


def compute_audio_stats(audio, sr):
    audio = _clean_numeric_audio(audio)
    if len(audio) == 0:
        return {"duration_sec": 0.0, "peak": 0.0, "rms": 0.0, "zcr": 0.0}

    duration = len(audio) / sr
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))
    zcr = float(np.mean(np.abs(np.diff(np.sign(audio))) > 0))

    return {
        "duration_sec": round(duration, 4),
        "peak": round(peak, 4),
        "rms": round(rms, 4),
        "zcr": round(zcr, 4),
    }


def evaluate_audio_quality(
    stats,
    min_duration=0.25,
    max_duration=6.0,
    min_rms=0.005,
    max_peak=0.99,
):
    issues = []
    duration = float(stats.get("duration_sec", 0.0))
    peak = float(stats.get("peak", 0.0))
    rms = float(stats.get("rms", 0.0))

    if duration < min_duration:
        issues.append("Speech too short")
    if duration > max_duration:
        issues.append("Speech too long")
    if rms < min_rms:
        issues.append("Signal too weak")
    if peak > max_peak:
        issues.append("Possible clipping")

    return {"ok": len(issues) == 0, "issues": issues}
