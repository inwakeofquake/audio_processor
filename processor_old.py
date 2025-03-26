import whisper
import torch
from docx import Document

def transcribe_russian_audio():
    # 1. Setup GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # 2. Load Model
    model = whisper.load_model("large").to(device)
    
    # 3. Transcribe with Russian language forced
    result = model.transcribe(
        "bod_day_2.m4a",
        language="ru",  # Force Russian language
        task="transcribe",  # Disable auto-translation
        fp16=torch.cuda.is_available(),  # GPU optimization
        verbose=False  # Disable live console output
    )
    
    # 4. Save Original Russian Text
    original_text = result["text"]
    doc = Document()
    doc.add_paragraph(original_text)
    doc.save("bod_day_2.docx")
    print("Russian transcription saved successfully!")

if __name__ == "__main__":
    transcribe_russian_audio()