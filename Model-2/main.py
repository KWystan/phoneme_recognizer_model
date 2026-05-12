import io
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from model.phoneme_recognizer import recognizer
from modules.audio_processor import clean_and_prepare_audio
from modules.panphon_module import align_and_score

app = FastAPI()

@app.post("/assess")
async def assess_pronunciation(word: str = Form(...), file: UploadFile = File(...)):
    # 1. Read and Reset Audio Buffer
    content = await file.read()
    buffer = io.BytesIO(content)
    
    # 2. Extract Audio Array and Stats
    clean_audio, quality, stats = clean_and_prepare_audio(buffer)

    if not quality["ok"]:
        return {"error": "Invalid Audio", "details": quality["issues"]}
    
    # 3. Get the sounds actually heard (Detected)
    detected_ipa = recognizer.transcribe_to_ipa(clean_audio)
    
    # 4. Get the correct sounds for the word (Expected)
    expected_ipa = recognizer.word_to_ipa(word)
    
    # 5. Score the difference
    assessment = align_and_score(expected_ipa, detected_ipa)

    return {
        "target_word": word,
        "expected_ipa": expected_ipa,
        "detected_ipa": detected_ipa,
        "assessment": assessment,
        "stats": stats
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)