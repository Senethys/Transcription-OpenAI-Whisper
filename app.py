import tkinter as tk
from tkinter import filedialog, ttk
import whisper
from pydub import AudioSegment
from pydub.utils import which
import os
from datetime import datetime
import threading

AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

class VideoTranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Transcriber")
        self.root.geometry("600x400")
        
        # Initialize Whisper model
        self.model = whisper.load_model("base")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Upload button
        self.upload_btn = ttk.Button(
            self.main_frame,
            text="Select Video",
            command=self.upload_video
        )
        self.upload_btn.grid(row=0, column=0, pady=10)
        
        # File path label
        self.file_label = ttk.Label(self.main_frame, text="No file selected")
        self.file_label.grid(row=1, column=0, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.grid(row=2, column=0, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="")
        self.status_label.grid(row=3, column=0, pady=5)
        
        # Transcription text area
        self.text_area = tk.Text(self.main_frame, height=15, width=60)
        self.text_area.grid(row=4, column=0, pady=10)
        
        # Save button
        self.save_btn = ttk.Button(
            self.main_frame,
            text="Save Transcription",
            command=self.save_transcription,
            state="disabled"
        )
        self.save_btn.grid(row=5, column=0, pady=10)
        
    def update_ui(self, status_text=None, progress_value=None, enable_save=None):
        """Safely update UI elements from any thread"""
        def _update():
            if status_text is not None:
                self.status_label.config(text=status_text)
            if progress_value is not None:
                self.progress["value"] = progress_value
            if enable_save is not None:
                self.save_btn["state"] = "normal" if enable_save else "disabled"
        self.root.after(0, _update)

    def update_text(self, text):
        """Safely update text area from any thread"""
        def _update():
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, text)
        self.root.after(0, _update)
        
    def upload_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        
        if file_path:
            self.file_label.config(text=os.path.basename(file_path))
            self.update_ui(status_text="Processing video...", progress_value=0, enable_save=False)
            self.update_text("")
            
            # Start transcription in a separate thread
            thread = threading.Thread(target=self.transcribe_video, args=(file_path,), daemon=True)
            thread.start()
    
    def transcribe_video(self, video_path):
        try:
            # Extract audio from video
            self.update_ui(status_text="Extracting audio...", progress_value=20)
            
            # Convert video to audio using pydub
            audio = AudioSegment.from_file(video_path)
            audio_path = "temp_audio.mp3"
            audio.export(audio_path, format="mp3")
            
            # Transcribe audio
            self.update_ui(status_text="Transcribing audio...", progress_value=40)
            
            result = self.model.transcribe(audio_path)
            
            # Update UI with transcription
            self.update_text(result["text"])
            
            # Clean up
            os.remove(audio_path)
            
            self.update_ui(status_text="Transcription complete!", progress_value=100, enable_save=True)
            
        except Exception as e:
            self.update_ui(status_text=f"Error: {str(e)}", progress_value=0, enable_save=False)
    
    def save_transcription(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"transcription_{timestamp}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.status_label.config(text="Transcription saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTranscriberApp(root)
    root.mainloop()