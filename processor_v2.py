import whisper
import torch
from docx import Document
import os
import time
from pathlib import Path
import platform
import psutil

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_hardware_info():
    """Get detailed hardware information"""
    system = platform.system()
    processor = platform.processor()
    memory = psutil.virtual_memory()
    
    log(f"System: {system}")
    log(f"Processor: {processor}")
    log(f"Total RAM: {memory.total / (1024**3):.2f} GB")
    
    if torch.cuda.is_available():
        log(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        log(f"CUDA Version: {torch.version.cuda}")
    elif torch.backends.mps.is_available():
        log("MPS (Metal) available for Apple Silicon")
    else:
        log("Using CPU")

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

def get_device():
    """Determine the best available device for processing"""
    # Temporarily force CPU usage due to MPS limitations
    return "cpu"
    # Original code commented out for future reference
    # if torch.cuda.is_available():
    #     return "cuda"
    # elif torch.backends.mps.is_available():
    #     return "mps"
    # return "cpu"

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
    device = get_device()
    get_hardware_info()
    log(f"Using device: {device.upper()}")
    
    # Load model with optimized settings
    log("Loading Whisper model...")
    try:
        model = whisper.load_model(
            "large",
            device="cpu",  # Force CPU usage
            download_root="./models",
            in_memory=True
        )
    except Exception as e:
        log(f"Failed to load model: {e}")
        return

    # Transcription setup with optimized parameters
    params = {
        "language": "ru",
        "task": "transcribe",
        "fp16": False,  # Disable FP16 when using CPU
        "verbose": False,  # Disable verbose output
        "temperature": 0.2,  # Slightly increased temperature for more variation
        "best_of": 3,  # Take best of multiple decodings
        "beam_size": 5,  # Use beam search for more stable results
        "compression_ratio_threshold": 1.8,  # Reduced from 2.4 to be less aggressive
        "condition_on_previous_text": False,  # Don't condition on previous text to avoid loops
        "no_speech_threshold": 0.4  # Slightly reduced to be less sensitive
    }

    # Progress monitoring
    start_time = time.time()
    last_memory_check = time.time()
    total_duration = None
    
    def log_progress():
        nonlocal last_memory_check, total_duration
        current_time = time.time()
        if current_time - last_memory_check >= 1.0:  # Update every second
            memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            elapsed = current_time - start_time
            
            # Try to get total duration from the audio file
            if total_duration is None:
                try:
                    import ffmpeg
                    probe = ffmpeg.probe(audio_path)
                    total_duration = float(probe['format']['duration'])
                except:
                    total_duration = 0
            
            if total_duration > 0:
                progress = min(100, (elapsed / total_duration) * 100)
                log(f"Progress: {progress:.1f}% (Memory: {memory:.1f}MB, Time: {elapsed:.1f}s)")
            else:
                log(f"Processing... (Memory: {memory:.1f}MB, Time: {elapsed:.1f}s)")
            
            last_memory_check = current_time

    # Run transcription
    log(f"Starting transcription of {Path(audio_file).name}...")
    try:
        # Start a timer to monitor progress
        import threading
        stop_progress = False
        
        def progress_monitor():
            while not stop_progress:
                log_progress()
                time.sleep(1)
        
        progress_thread = threading.Thread(target=progress_monitor)
        progress_thread.start()
        
        # Redirect stdout temporarily to suppress Whisper's output
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        result = model.transcribe(
            audio_path,
            **params
        )
        
        # Restore stdout
        sys.stdout = old_stdout
        
        # Stop the progress monitor
        stop_progress = True
        progress_thread.join()
        
    except Exception as e:
        stop_progress = True
        sys.stdout = old_stdout  # Ensure stdout is restored even if there's an error
        log(f"Transcription failed: {e}")
        return

    # Save results
    try:
        doc = Document()
        doc.add_paragraph(result["text"])
        doc.save(docx_file)
        total_time = time.time() - start_time
        log(f"Success! Transcript saved to {docx_file}")
        log(f"Total processing time: {total_time:.1f} seconds")
        print("\n" + "="*50)
        print(f"File saved to: {Path(docx_file).resolve()}")
        print("="*50 + "\n")
    except Exception as e:
        log(f"Failed to save document: {e}")

if __name__ == "__main__":
    transcribe_audio()