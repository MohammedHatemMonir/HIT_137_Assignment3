# Custom GUI widgets for the app

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional
from PIL import Image, ImageTk


class ValidatedEntry(tk.Entry):
    # Text entry with validation
    
    def __init__(self, parent, validation_callback: Optional[Callable] = None, **kwargs):
        # Set up the entry widget
        super().__init__(parent, **kwargs)
        self._validation_callback = validation_callback
        self._original_bg = self.cget('bg')
        
        # Bind validation events
        self.bind('<KeyRelease>', self._on_text_change)
        self.bind('<FocusOut>', self._on_focus_lost)
    
    def _on_text_change(self, event) -> None:
        # Check text as user types
        if self._validation_callback:
            is_valid = self._validation_callback(self.get())
            self._update_appearance(is_valid)
    
    def _on_focus_lost(self, event) -> None:
        # Check text when user clicks away
        if self._validation_callback:
            is_valid = self._validation_callback(self.get())
            self._update_appearance(is_valid)
    
    def _update_appearance(self, is_valid: bool) -> None:
        # Change colors based on validation
        if is_valid:
            self.config(bg=self._original_bg)
        else:
            self.config(bg='#ffcccc')  # Light red for invalid input
    
    def is_valid(self) -> bool:
        """Check if current input is valid - encapsulated validation."""
        if self._validation_callback:
            return self._validation_callback(self.get())
        return True


class ImageDisplayFrame(tk.Frame):
    # Frame for showing images
    
    def __init__(self, parent, max_width: int = 400, max_height: int = 400, **kwargs):
        # Set up image display area
        super().__init__(parent, **kwargs)
        
        # Store max size settings
        self._max_width = max_width
        self._max_height = max_height
        self._current_image = None
        self._current_photo = None
        
        # Create image label
        self._image_label = tk.Label(
            self,
            text="No image loaded",
            bg="lightgray",
            relief=tk.SUNKEN,
            compound=tk.CENTER
        )
        self._image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set minimum size for the frame
        self.config(width=self._max_width, height=self._max_height)
        self.pack_propagate(False)
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        # Resize image to fit in display area
        width, height = image.size
        
        # If image is smaller than max dimensions, don't resize
        if width <= self._max_width and height <= self._max_height:
            return image
        
        # Calculate scaling to fit within max dimensions
        scale_w = self._max_width / width
        scale_h = self._max_height / height
        scale = min(scale_w, scale_h)  # Use smallest scale to fit both dimensions
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def display_image(self, image: Image.Image) -> None:
        """
        Display image in the frame - encapsulated display logic.
        
        Args:
            image: PIL Image to display
        """
        try:
            # Store original image
            self._current_image = image.copy()
            
            # Resize image for display
            display_image = self._resize_image(image)
            
            # Convert to PhotoImage for Tkinter
            self._current_photo = ImageTk.PhotoImage(display_image)
            
            # Update label
            self._image_label.config(
                image=self._current_photo,
                text="",
                bg="white"
            )
            
        except Exception as e:
            self._show_error(f"Failed to display image: {str(e)}")
    
    def _show_error(self, message: str) -> None:
        """Private method to show error message - encapsulation."""
        self._image_label.config(
            image="",
            text=f"Error: {message}",
            bg="lightcoral"
        )
        self._current_photo = None
    
    def clear_image(self) -> None:
        """Clear displayed image - encapsulated state management."""
        self._current_image = None
        self._current_photo = None
        self._image_label.config(
            image="",
            text="No image loaded",
            bg="lightgray"
        )
    
    def get_current_image(self) -> Optional[Image.Image]:
        """Get currently displayed image - encapsulated access."""
        return self._current_image


class StatusBar(tk.Frame):
    # Bottom status bar
    
    def __init__(self, parent, **kwargs):
        """Initialize status bar."""
        super().__init__(parent, relief=tk.SUNKEN, bd=1, **kwargs)
        
        # Status label
        self._status_label = tk.Label(
            self,
            text="Ready",
            anchor=tk.W,
            padx=5
        )
        self._status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def set_status(self, message: str) -> None:
        # Update status message
        self._status_label.config(text=message)
        self.update_idletasks()


class ScrollableInfoFrame(tk.Frame):
    # Text area with scroll bar
    
    def __init__(self, parent, title: str = "Information", **kwargs):
        """
        Initialize scrollable info frame.
        
        Args:
            parent: Parent widget
            title: Frame title
        """
        super().__init__(parent, **kwargs)
        
        # Title label
        title_label = tk.Label(self, text=title, font=('Arial', 10, 'bold'))
        title_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        # Scrollable text widget
        self._text_widget = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            height=12,
            state=tk.DISABLED,
            font=('Arial', 9)
        )
        self._text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def set_content(self, content: str) -> None:
        """Set text content - encapsulated text management."""
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.delete(1.0, tk.END)
        self._text_widget.insert(tk.END, content)
        self._text_widget.config(state=tk.DISABLED)
    
    def append_content(self, content: str) -> None:
        """Append text content - encapsulated text management."""
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.insert(tk.END, content)
        self._text_widget.config(state=tk.DISABLED)
        self._text_widget.see(tk.END)  # Scroll to bottom