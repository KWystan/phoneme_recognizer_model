import sys
import torch
import numpy as np
import torchaudio

# --- UNIVERSAL TORCHAUDIO BRIDGE ---
# This version dynamically finds AudioMetaData regardless of torchaudio version
if not hasattr(torchaudio, 'backend'):
    from types import ModuleType
    
    # 1. Create the dummy path DeepFilterNet expects
    backend = ModuleType('backend')
    common = ModuleType('common')
    sys.modules['torchaudio.backend'] = backend
    sys.modules['torchaudio.backend.common'] = common
    
    # 2. Find AudioMetaData (it moves between versions)
    meta = None
    for loc in [torchaudio, torchaudio.utils, getattr(torchaudio, 'metadata', None)]:
        if hasattr(loc, 'AudioMetaData'):
            meta = getattr(loc, 'AudioMetaData')
            break
    
    # 3. Fallback: If we still can't find it, define a dummy class so it doesn't crash
    if meta is None:
        class AudioMetaData:
            def __init__(self, sample_rate, num_frames, num_channels, bits_per_sample, encoding):
                self.sample_rate = sample_rate
                self.num_frames = num_frames
                self.num_channels = num_channels
        meta = AudioMetaData
        
    common.AudioMetaData = meta

# --- NOW THE STANDARD IMPORTS ---
from df.enhance import init_df, enhance
from silero_vad import load_silero_vad, get_speech_timestamps

# Initialize device and models
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
df_model, df_state, _ = init_df()
vad_model = load_silero_vad().to(device)

def apply_deep_denoise(audio: np.ndarray) -> np.ndarray:
    """A gentler version of denoising to stop eating child consonants."""
    if len(audio) == 0: return audio
    
    audio_pt = torch.from_numpy(audio).unsqueeze(0)
    
    # We mix the 'enhanced' audio with a bit of the 'original' audio (Dry/Wet mix)
    # This ensures that even if the AI thinks /f/ is noise, some of it survives.
    enhanced = enhance(df_model, df_state, audio_pt).numpy().squeeze()
    
    # 80% Enhanced, 20% Original - This 'saves' soft consonants
    return (0.8 * enhanced) + (0.2 * audio)

def apply_silero_vad(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    if len(audio) == 0: return audio
    audio_pt = torch.from_numpy(audio)
    
    # Lower threshold (0.2) makes it MUCH more sensitive to soft sounds
    segments = get_speech_timestamps(audio_pt, vad_model, sampling_rate=sr, threshold=0.2)
    
    if not segments: return audio
        
    # Increase padding to 400ms to be safe
    padding = int(sr * 0.4) 
    start = max(0, segments[0]['start'] - padding)
    end = min(len(audio), segments[-1]['end'] + padding)
    return audio[start:end]