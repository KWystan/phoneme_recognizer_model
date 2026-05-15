import pandas as pd
from datasets import Dataset, Audio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, TrainingArguments, Trainer
import torch

# 1. SETUP DATASET
# Assumes a metadata.csv with columns: 'file_path' and 'text' (IPA phonemes)
data = pd.read_csv("metadata.csv") 
dataset = Dataset.from_pandas(data)
dataset = dataset.cast_column("file_path", Audio(sampling_rate=16000))

# 2. LOAD PREPARER
model_id = "facebook/wav2vec2-lv-60-espeak-cv-ft"
# Use the manual loading logic we established to avoid eSpeak errors
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2PhonemeCTCTokenizer
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_id)
tokenizer = Wav2Vec2PhonemeCTCTokenizer.from_pretrained(model_id, do_phonemize=False)
processor = Wav2Vec2Processor(feature_extractor=feature_extractor, tokenizer=tokenizer)

# 3. PRE-PROCESS FUNCTION
def prepare_dataset(batch):
    audio = batch["file_path"]
    batch["input_values"] = processor(audio["array"], sampling_rate=audio["sampling_rate"]).input_values[0]
    with processor.as_target_processor():
        batch["labels"] = processor(batch["text"]).input_ids
    return batch

dataset = dataset.map(prepare_dataset, remove_columns=dataset.column_names)

# 4. LOAD MODEL
model = Wav2Vec2ForCTC.from_pretrained(
    model_id, 
    ctc_loss_reduction="mean", 
    pad_token_id=processor.tokenizer.pad_token_id,
)

# FREEZE FEATURE EXTRACTOR (Important!)
# This prevents the model from losing its general hearing ability
model.freeze_feature_extractor()

# 5. TRAINING ARGUMENTS
training_args = TrainingArguments(
    output_dir="./finetuned_phoneme_model",
    group_by_length=True,
    per_device_train_batch_size=4,
    evaluation_strategy="no",
    num_train_epochs=10,      # Adjust based on dataset size
    fp16=torch.cuda.is_available(),
    learning_rate=1e-5,       # Very low to prevent "breaking" the model
    save_steps=500,
)

# 6. INITIALIZE TRAINER
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=processor.feature_extractor,
)

# 7. START
print("Starting Fine-tuning...")
trainer.train()
trainer.save_model("./finetuned_phoneme_model")
print("Training Complete!")