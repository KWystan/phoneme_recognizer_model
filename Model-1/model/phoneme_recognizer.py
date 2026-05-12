from modules.ipa_converter import to_ipa

try:
    from g2p_en import G2p
    _G2P = G2p()
except Exception:
    _G2P = None


class PhonemeRecognizer:
    def __init__(self, model_name: str = "facebook/wav2vec2-base-960h", device: str | None = None):
        self.model_name = model_name
        self.device = device
        self.processor = None
        self.model = None
        self.g2p = _G2P

    def _ensure_loaded(self):
        if self.model is not None and self.processor is not None:
            return
        # Lazy import and load to avoid blocking app startup
        from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            # Use ignore_mismatched_sizes if available to reduce warnings
            try:
                self.model = Wav2Vec2ForCTC.from_pretrained(self.model_name, ignore_mismatched_sizes=True)
            except TypeError:
                self.model = Wav2Vec2ForCTC.from_pretrained(self.model_name)
            if self.device:
                try:
                    import torch
                    self.model.to(self.device)
                except Exception:
                    pass
        except Exception:
            # keep attributes None and re-raise so callers can handle errors
            self.processor = None
            self.model = None
            raise

    def transcribe(self, processed_audio_array):
        self._ensure_loaded()
        import torch
        inputs = self.processor(processed_audio_array, return_tensors="pt", sampling_rate=16000).input_values
        with torch.no_grad():
            logits = self.model(inputs).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0].lower()
        return transcription

    def get_ipa(self, processed_audio_array):
        transcription = self.transcribe(processed_audio_array)
        return to_ipa(transcription)

    def get_phonemes(self, processed_audio_array):
        transcription = self.transcribe(processed_audio_array)
        if self.g2p:
            return [p for p in self.g2p(transcription) if p.strip()]
        return transcription.split()


recognizer = PhonemeRecognizer()