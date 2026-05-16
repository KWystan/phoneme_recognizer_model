import numpy as np

def compute_audio_stats(audio, sr):
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

def evaluate_audio_quality(stats, min_duration=0.25, max_duration=3.0,
                           min_rms=0.01, max_peak=0.99):
    issues = []
    if stats["duration_sec"] < min_duration: issues.append("Speech too short")
    if stats["duration_sec"] > max_duration: issues.append("Speech too long")
    if stats["rms"] < min_rms:               issues.append("Signal too weak")
    if stats["peak"] > max_peak:             issues.append("Possible clipping")

    return {"ok": len(issues) == 0, "issues": issues}