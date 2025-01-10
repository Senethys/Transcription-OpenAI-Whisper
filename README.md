# Video Transcriber

## Overview
The Video Transcriber is a Python application that uses OpenAI's Whisper model to transcribe audio from video files. It provides a graphical user interface (GUI) built with Tkinter, allowing users to select video files, transcribe them, and save the transcriptions as text files.

## Features
- Select video files in various formats (e.g., MP4, AVI, MOV, MKV).
- Extract audio from video files using pydub.
- Transcribe audio using OpenAI's Whisper model.
- Save transcriptions as text files.

## Requirements
- Python 3.x
- Tkinter
- OpenAI Whisper
- pydub
- FFmpeg (must be installed and accessible in the system PATH)

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd OpenAI-Whisper-Transcriber
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   . venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure FFmpeg is installed and added to your system PATH.

## Usage
1. Run the application:
   ```bash
   python app.py
   ```
2. Use the GUI to select a video file.
3. Wait for the transcription to complete.
4. Save the transcription as a text file.

## Troubleshooting
- Ensure FFmpeg is installed and accessible in your system PATH if you encounter issues with audio extraction.
- Check that all required Python packages are installed in your virtual environment.

## License
This project is licensed under the MIT License. 