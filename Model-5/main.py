import torch

import os


import sys
import io

# GLOBAL FIX: Force UTF-8 for all I/O and set Environment Variable
os.environ["PYTHONUTF8"] = "1"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from model.phoneme_recognizer import recognizer
from modules.audio_processor import clean_and_prepare_audio
from modules.panphon_module import align_and_score
from phoneme_processes.engine import engine

app = FastAPI()

@app.post("/assess")
async def assess_pronunciation(word: str = Form(...), file: UploadFile = File(...)):
    # 1. Read Audio
    content = await file.read()
    buffer = io.BytesIO(content)
    
    # 2. Process Audio (Includes Resampling, VAD, Denoise, Normalization)
    clean_audio, quality, stats = clean_and_prepare_audio(buffer)

    if not quality["ok"]:
        return {"error": "Invalid Audio", "details": quality["issues"]}

    # 3. Transcribe and Get Target IPA
    detected_ipa = recognizer.transcribe_to_ipa(clean_audio)
    expected_ipa = recognizer.word_to_ipa(word)
    
    # 4. Alignment and Scoring
    assessment = align_and_score(expected_ipa, detected_ipa)

    # 5. Clinical Analysis (Uses Group-to-Group Logic)
    clinical_diagnostics = engine.analyze_diagnostics(assessment['breakdown'])

    return {
        "target_word": word,
        "expected_ipa": expected_ipa,
        "detected_ipa": detected_ipa,
        "overall_score": assessment['overall_score'],
        "assessment": {
            "phoneme_breakdown": assessment['breakdown'],
            "detected_processes": clinical_diagnostics
        },
        "stats": stats
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)