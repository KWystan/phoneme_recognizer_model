# main.py
import torch
import os
import sys
import io
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form

# --- SECURITY FIX: Fetch from Env Variable instead of hardcoding! ---
# Make sure to set this in your terminal or a .env file!
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

# GLOBAL FIX: Force UTF-8 for all I/O
os.environ["PYTHONUTF8"] = "1"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Your module imports
from model.phoneme_recognizer import recognizer
from modules.audio_processor import clean_and_prepare_audio
from modules.panphon_module import align_and_score
from phoneme_processes.engine import engine
from phoneme_processes.utils import tokenize_ipa

app = FastAPI()

@app.post("/assess")
async def assess_pronunciation(word: str = Form(...), file: UploadFile = File(...)):
    # 1. Read Audio
    content = await file.read()
    buffer = io.BytesIO(content)
    
    # 2. Process Audio
    clean_audio, quality, stats = clean_and_prepare_audio(buffer)

    if not quality["ok"]:
        return {"error": "Invalid Audio", "details": quality["issues"]}

    # 3. Transcribe and Get Target IPA Strings
    detected_ipa_string = recognizer.transcribe_to_ipa(clean_audio)
    expected_ipa_string = recognizer.word_to_ipa(word)
    
    # --- BUG FIX: TOKENIZE THE STRINGS HERE! ---
    expected_tokens = tokenize_ipa(expected_ipa_string)
    detected_tokens = tokenize_ipa(detected_ipa_string)
    
    # 4. Alignment and Scoring (Now safely using lists instead of raw strings)
    assessment = align_and_score(expected_tokens, detected_tokens)

    # 5. Clinical Analysis
    clinical_diagnostics = engine.analyze_diagnostics(assessment['breakdown'])

    return {
        "target_word": word,
        "expected_ipa": expected_ipa_string,
        "detected_ipa": detected_ipa_string,
        "overall_score": assessment['overall_score'],
        "assessment": {
            "phoneme_breakdown": assessment['breakdown'],
            "detected_processes": clinical_diagnostics
        },
        "stats": stats
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)