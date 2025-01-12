import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import whisper
from pydub import AudioSegment
from pydub.utils import which
import os
from datetime import datetime
import threading

# Set theme and style
def set_theme():
    style = ttk.Style()
    style.theme_use('clam')  # Using 'clam' theme for modern look
    
    # Configure colors
    style.configure('Main.TFrame', background='#f0f0f0')
    style.configure('Modern.TButton',
                   padding=10,
                   font=('Helvetica', 10),
                   background='#0078D4',
                   foreground='white')
    style.configure('Success.TButton',
                   padding=10,
                   font=('Helvetica', 10),
                   background='#28a745')
    style.configure('Modern.TLabel',
                   font=('Helvetica', 10),
                   background='#f0f0f0')
    style.configure('Title.TLabel',
                   font=('Helvetica', 12, 'bold'),
                   background='#f0f0f0')
    style.configure('Status.TLabel',
                   font=('Helvetica', 9),
                   foreground='#666666',
                   background='#f0f0f0')
    style.configure('Horizontal.TProgressbar',
                   background='#0078D4',
                   troughcolor='#f0f0f0',
                   bordercolor='#f0f0f0',
                   lightcolor='#0078D4',
                   darkcolor='#0078D4')

AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

class VideoTranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Transcriber")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Set theme
        set_theme()
        
        # Initialize Whisper model
        self.model = whisper.load_model("base")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="30", style='Main.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        self.title_label = ttk.Label(
            self.main_frame,
            text="Video to Text Transcription",
            style='Title.TLabel'
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Upload frame
        self.upload_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.upload_frame.grid(row=1, column=0, pady=(0, 20), sticky='ew')
        self.upload_frame.columnconfigure(1, weight=1)
        
        # Upload button with icon (you can add an icon here)
        self.upload_btn = ttk.Button(
            self.upload_frame,
            text="Select Video",
            command=self.upload_video,
            style='Modern.TButton'
        )
        self.upload_btn.grid(row=0, column=0, padx=(0, 10))
        
        # File path label with ellipsis if too long
        self.file_label = ttk.Label(
            self.upload_frame,
            text="No file selected",
            style='Modern.TLabel'
        )
        self.file_label.grid(row=0, column=1, sticky='w')
        
        # Progress frame
        self.progress_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.progress_frame.grid(row=2, column=0, pady=(0, 20), sticky='ew')
        self.progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            style='Horizontal.TProgressbar'
        )
        self.progress.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(
            self.progress_frame,
            text="Ready to transcribe",
            style='Status.TLabel'
        )
        self.status_label.grid(row=1, column=0, sticky='w')
        
        # Transcription frame
        self.transcription_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.transcription_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 20))
        self.transcription_frame.columnconfigure(0, weight=1)
        self.transcription_frame.rowconfigure(0, weight=1)
        
        # Transcription text area with scrollbar
        self.text_frame = ttk.Frame(self.transcription_frame, style='Main.TFrame')
        self.text_frame.grid(row=0, column=0, sticky='nsew')
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        
        self.text_area = tk.Text(
            self.text_frame,
            height=15,
            width=60,
            wrap=tk.WORD,
            font=('Helvetica', 10),
            bg='white',
            relief='flat'
        )
        self.text_area.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.text_frame,
            orient='vertical',
            command=self.text_area.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.text_area['yscrollcommand'] = self.scrollbar.set
        
        # Save button frame
        self.button_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.button_frame.grid(row=4, column=0, pady=(0, 10))
        
        # Save button
        self.save_btn = ttk.Button(
            self.button_frame,
            text="Save Transcription",
            command=self.save_transcription,
            state="disabled",
            style='Success.TButton'
        )
        self.save_btn.grid(row=0, column=0, padx=5)
        
        # Copy button
        self.copy_btn = ttk.Button(
            self.button_frame,
            text="Copy Text",
            command=self.copy_text,
            state="disabled",
            style='Modern.TButton'
        )
        self.copy_btn.grid(row=0, column=1, padx=5)
        
    def update_ui(self, status_text=None, progress_value=None, enable_save=None):
        """Safely update UI elements from any thread"""
        def _update():
            if status_text is not None:
                self.status_label.config(text=status_text)
            if progress_value is not None:
                self.progress["value"] = progress_value
            if enable_save is not None:
                self.save_btn["state"] = "normal" if enable_save else "disabled"
                self.copy_btn["state"] = "normal" if enable_save else "disabled"
                if enable_save:
                    self.save_btn.configure(style='Success.TButton')
        self.root.after(0, _update)

    def update_text(self, text):
        """Safely update text area from any thread"""
        def _update():
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, text)
        self.root.after(0, _update)
        
    def upload_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            if len(filename) > 40:
                display_name = filename[:37] + "..."
            else:
                display_name = filename
            self.file_label.config(text=display_name)
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
            
            self.update_ui(status_text="✓ Transcription complete!", progress_value=100, enable_save=True)
            
        except Exception as e:
            error_message = str(e)
            self.update_ui(
                status_text=f"Error: {error_message[:50]}{'...' if len(error_message) > 50 else ''}",
                progress_value=0,
                enable_save=False
            )
            messagebox.showerror("Error", str(e))
    
    def save_transcription(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            title="Save Transcription",
            defaultextension=".txt",
            initialfile=f"transcription_{timestamp}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.status_label.config(text="✓ Transcription saved successfully!")
                messagebox.showinfo("Success", "Transcription saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def copy_text(self):
        """Copy transcription text to clipboard"""
        text = self.text_area.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_label.config(text="✓ Text copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTranscriberApp(root)
    root.mainloop()