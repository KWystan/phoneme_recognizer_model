# Phoneme Scoring API

This project exposes a small FastAPI service that accepts a WAV audio file and a target word (or IPA) and returns a PanPhon raw distance score between the spoken audio and the target.

Quick start

1. Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Run the API locally:

```bash
uvicorn app:app --reload
```

3. POST to `/score` with multipart form data: `file` (wav) and `target` (word or IPA).

Notes
- The project converts English words to IPA using `eng_to_ipa` via `modules/ipa_converter.py`.
	If `eng_to_ipa` is not installed, `ipa_converter.to_ipa()` will return the input unchanged
	(treat the input as IPA directly in that case).
- The scoring uses PanPhon's feature-edit-distance per-phoneme (lower is better).