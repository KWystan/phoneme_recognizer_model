import re
import torch
import eng_to_ipa
from transformers import (
    Wav2Vec2ForCTC, 
    Wav2Vec2FeatureExtractor, 
    Wav2Vec2PhonemeCTCTokenizer, 
    Wav2Vec2Processor
)

class PhonemeRecognizer:
    def __init__(self):
        self.model_id = "facebook/wav2vec2-lv-60-espeak-cv-ft"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # This manual loading is the ONLY way to stop the crash 
        # caused by the library re-installation.
        feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(self.model_id)
        tokenizer = Wav2Vec2PhonemeCTCTokenizer.from_pretrained(
            self.model_id, 
            do_phonemize=False # This blocks the eSpeak check
        )
        
        # We manually plug them together so it doesn't "auto-search" for eSpeak
        self.processor = Wav2Vec2Processor(
            feature_extractor=feature_extractor, 
            tokenizer=tokenizer
        )
        
        self.model = Wav2Vec2ForCTC.from_pretrained(self.model_id).to(self.device)
        self.model.eval()
        print("--- Project Restored ---")

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"[^A-Za-z\s'-]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def transcribe_to_ipa(self, audio_array):
        inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        pred_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(pred_ids)[0]
        return transcription.replace(" ", "").replace("|", "").strip()

    def word_to_ipa(self, word):
        word = self._clean_text(word)
        if not word: return ""
        ipa = eng_to_ipa.convert(word)
        return ipa.replace("/", "").replace("ˈ", "").replace("ˌ", "").strip()

recognizer = PhonemeRecognizer()