import whisper
import torch
from docx import Document
import os
import time
from pathlib import Path

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_user_input():
    """Interactively get filenames from user"""
    print("\n" + "="*50)
    print("WHISPER AI AUDIO-TO-TEXT TOOL".center(50))
    print("="*50 + "\n")
    
    while True:
        audio_file = input("Enter audio file name in root directory (e.g., my_audio.m4a): ").strip()
        if not audio_file:
            print("Error: Filename cannot be empty")
            continue
            
        txt_file = input("Enter output DOCX filename (e.g., transcript.docx): ").strip()
        if not txt_file:
            print("Error: Output filename cannot be empty")
            continue
            
        # Add .docx extension if missing
        if not txt_file.lower().endswith('.docx'):
            txt_file += '.docx'
            
        return audio_file, txt_file

def validate_file(file_path):
    """Check if file exists and is valid"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in ['.m4a', '.mp3', '.wav', '.ogg', '.flac']:
        raise ValueError(f"Unsupported audio format: {path.suffix}")
    return str(path.resolve())

def transcribe_audio():
    # Get user input
    audio_file, docx_file = get_user_input()
    
    # Validate input file
    try:
        audio_path = validate_file(audio_file)
    except Exception as e:
        log(f"Error: {e}")
        return

    # Hardware setup
    device = "GPU" if torch.cuda.is_available() else "CPU"
    log(f"Using: {device.upper()} ({torch.cuda.get_device_name(0) if device == 'CUDA' else 'CPU'})")
    
    # Load model
    log("Loading Whisper model...")
    try:
        model = whisper.load_model(
            "large",
            device=device,
            download_root="./models",
            in_memory=True
        )
    except Exception as e:
        log(f"Failed to load model: {e}")
        return

    # Transcription setup
    params = {
        "language": "ru",
        "task": "transcribe",
        "fp16": torch.cuda.is_available(),
        "verbose": None,
        "temperature": 0.0
    }

    # Progress handler
    last_progress = 0
    def progress_callback(p):
        nonlocal last_progress
        current = int(p*100)
        if current > last_progress:
            log(f"Transcribing: {current}%")
            last_progress = current
        return True

    # Run transcription
    log(f"Starting transcription of {Path(audio_file).name}...")
    try:
        result = model.transcribe(
            audio_path,
            **params,
            callback=progress_callback
        )
    except Exception as e:
        log(f"Transcription failed: {e}")
        return

    # Save results
    try:
        doc = Document()
        doc.add_paragraph(result["text"])
        doc.save(docx_file)
        log(f"Success! Transcript saved to {docx_file}")
        print("\n" + "="*50)
        print(f"File saved to: {Path(docx_file).resolve()}")
        print("="*50 + "\n")
    except Exception as e:
        log(f"Failed to save document: {e}")

if __name__ == "__main__":
    transcribe_audio()