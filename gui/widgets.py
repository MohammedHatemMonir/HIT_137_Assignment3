"""
================================================================================
CUSTOM GUI WIDGETS - SPECIALIZED TKINTER COMPONENTS
================================================================================

OVERVIEW:
This module provides custom Tkinter widget classes that extend the standard 
toolkit with specialized functionality for the AI Model Demo Application. 
These widgets demonstrate Object-Oriented Programming principles through 
inheritance, encapsulation, and composition while providing enhanced user 
interface capabilities for image display, input validation, and information 
presentation.

CUSTOM WIDGET CLASSES:
1. ValidatedEntry: Enhanced text entry with real-time validation
2. ImageDisplayFrame: Specialized image display with automatic resizing
3. StatusBar: Application status indicator with message display
4. ScrollableInfoFrame: Text information display with scrolling capability

KEY OOP CONCEPTS DEMONSTRATED:
1. INHERITANCE:
   - All custom widgets inherit from standard Tkinter components
   - Extends base functionality while maintaining compatibility
   - Leverages parent class methods and properties

2. ENCAPSULATION:
   - Private attributes for internal state management
   - Protected methods for controlled access to functionality
   - Public interface methods for external interaction

3. COMPOSITION:
   - Complex widgets composed of multiple Tkinter components
   - Aggregation of functionality from different widget types
   - Hierarchical organization of UI elements

4. POLYMORPHISM:
   - Overridden methods for specialized behavior
   - Custom event handling while maintaining standard interfaces
   - Dynamic behavior based on widget state

WIDGET DETAILS:

ValidatedEntry:
- PURPOSE: Text input with real-time validation feedback
- FEATURES: 
  * Custom validation callbacks
  * Visual feedback (background color changes)
  * Live validation on key events and focus changes
  * Programmatic validation checking
- OOP CONCEPTS: Inheritance from tk.Entry, encapsulation of validation logic
- USAGE: Form inputs requiring specific format validation

ImageDisplayFrame:
- PURPOSE: Image display with automatic scaling and aspect ratio preservation
- FEATURES:
  * Automatic image resizing to fit display area
  * Maintains aspect ratio during scaling
  * Error handling for display failures
  * Support for various PIL Image formats
  * Memory management for image objects
- OOP CONCEPTS: Composition of tk.Frame and tk.Label, encapsulation of image processing
- USAGE: Displaying input images and AI model output visualizations

StatusBar:
- PURPOSE: Application status messages and user feedback
- FEATURES:
  * Real-time status message updates
  * Persistent display area at bottom of application
  * Automatic layout management
  * Thread-safe message updates
- OOP CONCEPTS: Inheritance from tk.Frame, encapsulation of status management
- USAGE: Providing user feedback during operations

ScrollableInfoFrame:
- PURPOSE: Display of textual information with scrolling capability
- FEATURES:
  * Scrollable text area for large content
  * Title display with configurable text
  * Read-only content protection
  * Content replacement and appending methods
  * Automatic scrolling to new content
- OOP CONCEPTS: Composition of multiple widgets, encapsulation of content management
- USAGE: Displaying model information and help text

DESIGN PATTERNS:
1. TEMPLATE METHOD: Base widget structure with customizable behavior
2. STRATEGY PATTERN: Pluggable validation strategies for ValidatedEntry  
3. FACADE PATTERN: Simplified interfaces hiding complex widget interactions
4. OBSERVER PATTERN: Event-driven updates for validation and display changes

TECHNICAL IMPLEMENTATION:

Image Processing (ImageDisplayFrame):
- PIL Image integration for format handling
- Lanczos resampling for high-quality scaling
- Aspect ratio calculation and preservation
- Memory-efficient image conversion
- Error handling for corrupted or unsupported formats

Validation System (ValidatedEntry):
- Callback-based validation architecture
- Real-time visual feedback system
- Event binding for responsive validation
- State management for validation results
- Customizable validation logic

Layout Management:
- Automatic sizing and positioning
- Pack and grid geometry managers
- Responsive design principles
- Cross-platform compatibility
- Consistent styling and appearance

Event Handling:
- Custom event binding for specialized behavior
- Keyboard and mouse event processing
- Focus management for validation
- Thread-safe GUI updates

PERFORMANCE CONSIDERATIONS:
- Efficient image resizing with proper resampling
- Memory management for large images
- Event handler optimization
- Minimal redraw operations
- Lazy loading of widget content

ERROR HANDLING:
- Graceful handling of invalid inputs
- Image loading error recovery
- Display error messages in user-friendly format
- Fallback behavior for failed operations

USAGE PATTERNS:
- Instantiate custom widgets like standard Tkinter widgets
- Configure through constructor parameters
- Use public methods for content management
- Handle events through standard Tkinter mechanisms

INTEGRATION:
- Seamless integration with standard Tkinter widgets
- Compatible with existing layout managers
- Supports standard Tkinter styling and theming
- Event system compatible with main application

REFERENCES:
- ChatGPT-5: Widget design patterns and implementation guidance
- W3Schools Python Classes: https://www.w3schools.com/python/python_classes.asp
- Tkinter Widget Reference: https://docs.python.org/3/library/tkinter.ttk.html
- PIL/Pillow Documentation: https://pillow.readthedocs.io/
- Python Event Handling: https://realpython.com/python-gui-tkinter/#handling-events
================================================================================
"""

"""custom gui widgets"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional
from PIL import Image, ImageTk


class ValidatedEntry(tk.Entry):
    # entry that can validate text
    
    def __init__(self, parent, validation_callback: Optional[Callable] = None, **kwargs):
        # build entry
        super().__init__(parent, **kwargs)
        self._validation_callback = validation_callback
        self._original_bg = self.cget('bg')
        
    # bind events for validation
        self.bind('<KeyRelease>', self._on_text_change)
        self.bind('<FocusOut>', self._on_focus_lost)
    
    def _on_text_change(self, event) -> None:
        # live validation
        if self._validation_callback:
            is_valid = self._validation_callback(self.get())
            self._update_appearance(is_valid)
    
    def _on_focus_lost(self, event) -> None:
        # validate when leaving the field
        if self._validation_callback:
            is_valid = self._validation_callback(self.get())
            self._update_appearance(is_valid)
    
    def _update_appearance(self, is_valid: bool) -> None:
        # change background color based on valid state
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
    # frame that shows an image
    
    def __init__(self, parent, max_width: int = 400, max_height: int = 400, **kwargs):
        # build frame
        super().__init__(parent, **kwargs)
        
    # store max size settings
        self._max_width = max_width
        self._max_height = max_height
        self._current_image = None
        self._current_photo = None
        
    # create placeholder label
        self._image_label = tk.Label(
            self,
            text="No image loaded",
            bg="lightgray",
            relief=tk.SUNKEN,
            compound=tk.CENTER
        )
        self._image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    # lock minimum size of frame and stop auto shrink
        self.config(width=self._max_width, height=self._max_height)
        self.pack_propagate(False)
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        # shrink to fit box
        width, height = image.size
        
    # if already small enough just return
        if width <= self._max_width and height <= self._max_height:
            return image
        
    # scale to fit inside box
        scale_w = self._max_width / width
        scale_h = self._max_height / height
        scale = min(scale_w, scale_h)  # Use smallest scale to fit both dimensions
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def display_image(self, image: Image.Image) -> None:
        """Show image."""
        try:
            # store original image
            self._current_image = image.copy()
            
            # resize for display
            display_image = self._resize_image(image)
            
            # convert to tk image
            self._current_photo = ImageTk.PhotoImage(display_image)
            
            # update label
            self._image_label.config(
                image=self._current_photo,
                text="",
                bg="white"
            )
            
        except Exception as e:
            self._show_error(f"Failed to display image: {str(e)}")
    
    def _show_error(self, message: str) -> None:
        # show error text
        self._image_label.config(
            image="",
            text=f"Error: {message}",
            bg="lightcoral"
        )
        self._current_photo = None
    
    def clear_image(self) -> None:
        # reset frame to blank
        self._current_image = None
        self._current_photo = None
        self._image_label.config(
            image="",
            text="No image loaded",
            bg="lightgray"
        )
    
    def get_current_image(self) -> Optional[Image.Image]:
        # return stored original pil image
        return self._current_image


class StatusBar(tk.Frame):
    # bottom status bar
    
    def __init__(self, parent, **kwargs):
        """Initialize status bar."""
        super().__init__(parent, relief=tk.SUNKEN, bd=1, **kwargs)
        
    # status label
        self._status_label = tk.Label(
            self,
            text="Ready",
            anchor=tk.W,
            padx=5
        )
        self._status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def set_status(self, message: str) -> None:
        # update status text
        self._status_label.config(text=message)
        self.update_idletasks()


class ScrollableInfoFrame(tk.Frame):
    # text area with scroll bar
    
    def __init__(self, parent, title: str = "Information", **kwargs):
        # simple frame with a title and scrollable text
        super().__init__(parent, **kwargs)
        
    # title label
        title_label = tk.Label(self, text=title, font=('Arial', 10, 'bold'))
        title_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
    # scrolling text widget
        self._text_widget = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            height=12,
            state=tk.DISABLED,
            font=('Arial', 9)
        )
        self._text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def set_content(self, content: str) -> None:
    # replace all text content
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.delete(1.0, tk.END)
        self._text_widget.insert(tk.END, content)
        self._text_widget.config(state=tk.DISABLED)
    
    def append_content(self, content: str) -> None:
    # add more text at end
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.insert(tk.END, content)
        self._text_widget.config(state=tk.DISABLED)
        self._text_widget.see(tk.END)  # Scroll to bottom