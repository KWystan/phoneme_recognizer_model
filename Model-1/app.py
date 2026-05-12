from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import tempfile
import os

from modules.audio_processor import clean_and_prepare_audio
from model.phoneme_recognizer import recognizer
from modules.ipa_aligner import score_ipa_sequences
from modules.ipa_converter import to_ipa

app = FastAPI(title="Phoneme Scoring API")


@app.post("/score")
async def score(file: UploadFile = File(...), target: str = Form(...)):
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        temp_name = tmp.name
        content = await file.read()
        tmp.write(content)
    try:
        audio = clean_and_prepare_audio(temp_name)
        spoken_ipa = recognizer.get_ipa(audio)

        # Convert the provided target word to IPA when possible. If conversion
        # is not available, `to_ipa` will return the original string which the
        # scoring function will treat as an IPA-like input.
        target_ipa = to_ipa(target)

        try:
            result = score_ipa_sequences(target_ipa, spoken_ipa)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return {
            "target": target,
            "target_ipa": target_ipa,
            "spoken_ipa": spoken_ipa,
            "raw_score": result["raw_score"],
            "pairs": result["pairs"],
            "expected_len": result["expected_len"],
            "predicted_len": result["predicted_len"],
        }
    finally:
        try:
            os.remove(temp_name)
        except Exception:
            pass
