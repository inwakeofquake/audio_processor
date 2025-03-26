# Whisper AI Audio-to-Text Transcription Tool

A Python-based transcription utility that converts audio files to text documents using OpenAI's Whisper AI model. Supports multiple audio formats and provides interactive command-line interface.

## Features

- 🎙️ Supports common audio formats (M4A, MP3, WAV, OGG, FLAC)
- ⚡ GPU acceleration support (CUDA-enabled devices)
- 📈 Real-time progress tracking
- 📄 Automatic .docx extension handling
- ❗ Interactive file validation and error handling
- 🌐 Multi-language support (currently configured for Russian)
- ❗ Pure text output, no unnecessary timestamps

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- FFmpeg (must be available in system PATH)

### Dependencies
1. Install ffmpeg system dependency:

   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS (using Homebrew)
   brew install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg
## How to use the tool

- ### Install Python packages:

```bash
pip install torch whisper python-docx
```

- ### For GPU support (recommended), install PyTorch with CUDA:

```bash
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```

- ### Place your audio file in the project directory

- ### Run the script:

```bash
python whisper_transcriber.py
```

- ### Follow the interactive prompts:

```bash
===========================================
        WHISPER AI AUDIO-TO-TEXT TOOL           
===========================================

Enter audio file name in root directory (e.g., my_audio.m4a): recording.m4a
Enter output DOCX filename (e.g., transcript.docx): meeting_notes
```
- ### Wait for transcription to complete (progress shown in console)

- ### Find your transcript in the generated .docx file

### Example output:
```bash
[14:35:47] Using: GPU (NVIDIA GeForce RTX 5090)
[14:35:49] Loading Whisper model...
[14:36:02] Starting transcription of recording.m4a...
[14:36:03] Transcribing: 5%
[14:36:15] Transcribing: 78%
[14:36:21] Success! Transcript saved to meeting_notes.docx
```

## Important Notes
- The script uses Whisper's large model by default (requires ~3GB RAM)

- First run will download the AI model (≈3GB download)

- For better performance, ensure FFmpeg is properly installed (use Chocolatey on Windows)

- To change transcription language, modify language parameter in code

- Processing time varies by audio length and hardware (∼1x realtime on GPU)

## Troubleshooting
### FFmpeg not found:

- Verify installation with ffmpeg -version

- Add FFmpeg to system PATH if needed

### File not found errors:

- Ensure audio file is in project root directory

- Use full paths if needed (e.g., /home/user/audio.mp3)

### CUDA errors:

- Verify PyTorch CUDA installation: python -c "import torch; print(torch.cuda.is_available())"

- Or use cuda_check.py script in this repository

- Fallback to CPU by modifying device parameter in code

###  Unsupported formats:

- Convert files using FFmpeg: ffmpeg -i input.wma output.wav