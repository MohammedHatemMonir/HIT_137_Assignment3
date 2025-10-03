# Main GUI window for Assignment 3 - Basic Implementation

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
from pathlib import Path
from typing import Optional

from gui.widgets import ImageDisplayFrame, StatusBar, ScrollableInfoFrame
from gui.decorators import validate_input, log_operation, error_handler


class MainWindow(tk.Tk):
    # Main window class
    
    def __init__(self):
        # Set up the main window
        super().__init__()
        
        self._selected_image_path: Optional[str] = None
        
        self.title("Assignment 3 - AI Models Demo")
        self.state('zoomed')
        self.configure(bg='#f0f0f0')
        
        self._create_widgets()
        self._setup_layout()
        self._setup_event_handlers()
        
        print("[GUI] Application window initialized")
    
    def _create_widgets(self) -> None:
        # Create GUI widgets
        
        # Title label
        self.title_label = tk.Label(
            self,
            text="Assignment 3 - AI Models",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        
        # Mode selection frame
        self.mode_frame = tk.Frame(self, bg='#f0f0f0')
        self.mode_label = tk.Label(
            self.mode_frame,
            text="Select Mode:",
            font=('Arial', 12),
            bg='#f0f0f0'
        )
        
        # Mode selection
        self.mode_var = tk.StringVar(value="text_to_image")
        self.text_to_image_radio = tk.Radiobutton(
            self.mode_frame,
            text="Text to Image",
            variable=self.mode_var,
            value="text_to_image",
            bg='#f0f0f0',
            command=self._on_mode_change
        )
        
        self.image_to_caption_radio = tk.Radiobutton(
            self.mode_frame,
            text="Image to Caption",
            variable=self.mode_var,
            value="image_to_caption",
            bg='#f0f0f0',
            command=self._on_mode_change
        )
        
        # Main content frame
        self.main_frame = tk.Frame(self, bg='#f0f0f0')
        
        # Left panel for input/controls
        self.left_panel = tk.Frame(self.main_frame, bg='#f0f0f0')
        
        # Text input frame
        self.text_input_frame = tk.LabelFrame(
            self.left_panel,
            text="Text Input",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        )
        
        self.text_input = tk.Text(
            self.text_input_frame,
            height=4,
            width=50,
            wrap=tk.WORD,
            font=('Arial', 10)
        )
        
        # File selection frame
        self.file_frame = tk.LabelFrame(
            self.left_panel,
            text="Image File",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        )
        
        self.file_label = tk.Label(
            self.file_frame,
            text="No file selected",
            bg='#f0f0f0',
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5
        )
        
        self.browse_button = tk.Button(
            self.file_frame,
            text="Browse...",
            command=self._browse_for_image,
            bg='#e0e0e0'
        )
        
        # Process button
        self.process_button = tk.Button(
            self.left_panel,
            text="Process",
            command=self._process_request,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2
        )
        
        # Right panel for output
        self.right_panel = tk.Frame(self.main_frame, bg='#f0f0f0')
        
        # Image display
        self.image_display = ImageDisplayFrame(
            self.right_panel,
            max_width=400,
            max_height=400
        )
        
        # Output text area
        self.output_info = ScrollableInfoFrame(
            self.right_panel,
            title="Output Information"
        )
        
        # Status bar
        self.status_bar = StatusBar(self)
    
    def _setup_layout(self) -> None:
        # Arrange widgets in the window
        
        # Title
        self.title_label.pack(pady=(10, 5))
        
        # Mode selection
        self.mode_frame.pack(pady=5)
        self.mode_label.pack(side=tk.LEFT, padx=(0, 10))
        self.text_to_image_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.image_to_caption_radio.pack(side=tk.LEFT)
        
        # Main content
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Text input
        self.text_input_frame.pack(fill=tk.X, pady=(0, 10))
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        
        # File selection
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        self.file_label.pack(fill=tk.X, padx=5, pady=5)
        self.browse_button.pack(pady=(0, 5))
        
        # Process button
        self.process_button.pack(fill=tk.X, pady=10)
        
        # Right panel
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Image display
        self.image_display.pack(fill=tk.X, pady=(0, 10))
        
        # Output info
        self.output_info.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_event_handlers(self) -> None:
        # Set up event handlers
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_mode_change(self) -> None:
        # Handle mode selection change
        mode = self.mode_var.get()
        
        if mode == "text_to_image":
            self.text_input_frame.config(state=tk.NORMAL)
            self.file_frame.config(state=tk.DISABLED)
            self.status_bar.set_status("Mode: Text to Image - Enter text prompt")
        else:
            self.text_input_frame.config(state=tk.DISABLED)
            self.file_frame.config(state=tk.NORMAL)
            self.status_bar.set_status("Mode: Image to Caption - Select an image file")
    
    def _browse_for_image(self) -> None:
        # Browse for image file
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self._selected_image_path = file_path
            filename = Path(file_path).name
            self.file_label.config(text=filename)
            self.status_bar.set_status(f"Selected: {filename}")
    
    @validate_input
    @log_operation
    def _process_request(self) -> None:
        # Process user request
        mode = self.mode_var.get()
        
        try:
            if mode == "text_to_image":
                text_prompt = self.text_input.get("1.0", tk.END).strip()
                if not text_prompt:
                    messagebox.showwarning("Input Required", "Please enter a text prompt")
                    return
                
                self.status_bar.set_status("Processing: Text to Image (placeholder)")
                self.output_info.set_content(f"Text Prompt: {text_prompt}\\n\\nNote: AI model integration pending")
                
            elif mode == "image_to_caption":
                if not self._selected_image_path:
                    messagebox.showwarning("File Required", "Please select an image file")
                    return
                
                # Load and display image
                image = Image.open(self._selected_image_path)
                self.image_display.display_image(image)
                
                self.status_bar.set_status("Processing: Image to Caption (placeholder)")
                self.output_info.set_content(f"Image File: {Path(self._selected_image_path).name}\\n\\nNote: AI model integration pending")
            
            self.status_bar.set_status("Ready")
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.status_bar.set_status("Error occurred")
    
    def _on_closing(self) -> None:
        # Handle window closing
        print("[GUI] Application closing")
        self.destroy()