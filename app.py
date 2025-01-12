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
        self.root.title("Video Transcriber - OpenAI Whisper Base")
        
        # Set minimum and maximum window sizes
        self.root.minsize(600, 400)  # Increased minimum size to ensure buttons are visible
        self.root.maxsize(1200, 800)  # Maximum size to prevent too large windows
        
        # Initial size
        self.root.geometry("600x400")  # Increased initial size to match minimum
        self.root.configure(bg='#f0f0f0')
        
        # Configure main grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set theme
        set_theme()
        
        # Initialize Whisper model
        self.model = whisper.load_model("base")
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(3, weight=1)  # Make transcription frame expandable
        self.main_frame.grid_columnconfigure(0, weight=1)
        
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
        
        # Upload button with icon
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
        
        # Create but don't show transcription and button frames initially
        self.create_transcription_widgets()
        self.hide_transcription_widgets()
        
    def create_transcription_widgets(self):
        """Create transcription related widgets"""
        # Transcription frame
        self.transcription_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.transcription_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
        self.transcription_frame.grid_rowconfigure(0, weight=1)
        self.transcription_frame.grid_columnconfigure(0, weight=1)
        
        # Text frame with minimum height
        self.text_frame = ttk.Frame(self.transcription_frame, style='Main.TFrame')
        self.text_frame.grid(row=0, column=0, sticky='nsew')
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)
        
        # Text area with minimum height
        self.text_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=('Helvetica', 10),
            bg='white',
            relief='flat',
            height=10  # Minimum height in text lines
        )
        self.text_area.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.text_frame,
            orient='vertical',
            command=self.text_area.yview
        )
        self.text_area['yscrollcommand'] = self.scrollbar.set
        
        # Button frame at the bottom with fixed height
        self.button_frame = ttk.Frame(self.main_frame, style='Main.TFrame', height=50)
        self.button_frame.grid(row=4, column=0, sticky='ew', pady=(0, 5))
        self.button_frame.grid_propagate(False)  # Prevent frame from shrinking
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        
        # Center the buttons
        button_center = ttk.Frame(self.button_frame, style='Main.TFrame')
        button_center.grid(row=0, column=0, columnspan=2)
        
        # Save button
        self.save_btn = ttk.Button(
            button_center,
            text="Save Transcription",
            command=self.save_transcription,
            style='Success.TButton'
        )
        self.save_btn.grid(row=0, column=0, padx=5)
        
        # Copy button
        self.copy_btn = ttk.Button(
            button_center,
            text="Copy Text",
            command=self.copy_text,
            style='Modern.TButton'
        )
        self.copy_btn.grid(row=0, column=1, padx=5)

    def hide_transcription_widgets(self):
        """Hide transcription related widgets and shrink window"""
        # Hide widgets
        self.transcription_frame.grid_remove()
        self.button_frame.grid_remove()
        
        # Get current window position
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        
        # Set compact size while maintaining position
        self.root.geometry(f"600x400+{x}+{y}")  # Updated minimum size
        
        # Update window to ensure proper layout
        self.root.update_idletasks()

    def show_transcription_widgets(self):
        """Show transcription related widgets and resize window"""
        # Show widgets
        self.transcription_frame.grid()
        self.button_frame.grid()
        
        # Get current window position
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        
        # Calculate new size while maintaining position
        new_width = min(800, self.root.winfo_screenwidth() - 100)
        new_height = min(600, self.root.winfo_screenheight() - 100)
        
        # Set new geometry
        self.root.geometry(f"{new_width}x{new_height}+{x}+{y}")
        
        # Update window to ensure proper layout
        self.root.update_idletasks()

    def update_ui(self, status_text=None, progress_value=None, enable_save=None):
        """Safely update UI elements from any thread"""
        def _update():
            if status_text is not None:
                self.status_label.config(text=status_text)
            if progress_value is not None:
                self.progress["value"] = progress_value
            if enable_save is not None:
                if enable_save:
                    self.show_transcription_widgets()
                    self.save_btn.configure(style='Success.TButton')
                else:
                    self.hide_transcription_widgets()
        self.root.after(0, _update)

    def update_text(self, text):
        """Safely update text area from any thread"""
        def _update():
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, text)
            self.check_scrollbar()  # Check if scrollbar is needed after updating text
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

    def check_scrollbar(self, event=None):
        """Check if scrollbar is needed and show/hide accordingly"""
        self.text_area.tk.call('update', 'idletasks')  # Make sure sizes are up to date
        
        # Get the number of lines and visible lines
        total_lines = int(self.text_area.index('end-1c').split('.')[0])
        visible_lines = self.text_area.winfo_height() / self.text_area.dlineinfo('1.0')[3]
        
        if total_lines > visible_lines:
            self.scrollbar.grid(row=0, column=1, sticky='ns')
        else:
            self.scrollbar.grid_remove()
            
        # Reset the modified flag
        self.text_area.edit_modified(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTranscriberApp(root)
    root.mainloop()