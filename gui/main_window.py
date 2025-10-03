"""
================================================================================
MAIN GUI WINDOW - TKINTER APPLICATION INTERFACE
================================================================================

OVERVIEW:
This module contains the main graphical user interface for the AI Model Demo 
Application. It implements a comprehensive Tkinter-based GUI that provides 
user-friendly access to AI model functionalities including clothes segmentation 
and image captioning. The interface demonstrates advanced OOP principles through 
multiple inheritance, composition, and sophisticated event handling.

CORE FUNCTIONALITY:
- Dual-mode operation: Clothes Segmentation and Image Captioning
- Dynamic interface adaptation based on selected mode
- Real-time image processing with progress feedback
- Background threading for responsive user experience
- Comprehensive file handling (load/save images and text)
- Interactive model information display

GUI ARCHITECTURE:
The interface is organized into several key sections:
1. Title and Mode Selection (top)
2. Input Panel (left side) - image browsing and processing controls
3. Output Panel (right side) - results display and save options  
4. Information Panels (bottom) - model info and OOP concepts explanation

MAIN CLASSES:
1. ModelManager: Handles AI model lifecycle and processing
2. MainWindow: Main GUI class inheriting from tk.Tk and ModelManager

KEY OOP CONCEPTS DEMONSTRATED:
1. MULTIPLE INHERITANCE:
   - MainWindow inherits from both tk.Tk (GUI framework) and ModelManager (model handling)
   - Combines GUI capabilities with AI model management
   - Demonstrates diamond problem resolution in Python

2. COMPOSITION:
   - FileHandler for file operations
   - Custom widget classes embedded within main window
   - Model instances composed within ModelManager

3. ENCAPSULATION:
   - Private attributes and methods (underscore prefix)
   - Controlled access to model instances
   - Internal state management for GUI components

4. POLYMORPHISM:
   - Different processing behavior based on selected mode
   - Runtime method selection for model operations
   - Event handler polymorphism for different UI actions

5. DECORATOR PATTERN:
   - Function decorators for validation, logging, and error handling
   - Decorators applied to key processing methods
   - Cross-cutting concerns handled through decorators

GUI COMPONENTS:
- Custom ImageDisplayFrame widgets for image visualization
- ScrollableInfoFrame for displaying textual information
- Mode selection ComboBox for switching between AI models
- Dynamic button states based on application state
- Progress indication during model processing

THREADING ARCHITECTURE:
- Main GUI thread for interface responsiveness
- Background worker threads for AI model processing
- Thread-safe GUI updates using tkinter's after() method
- Proper thread synchronization and cleanup

MODE OPERATIONS:
1. CLOTHES SEGMENTATION MODE:
   - Load image and display original
   - Process through SegFormer model
   - Display overlay and colored segmentation maps
   - Save overlay and colored maps separately

2. IMAGE CAPTIONING MODE:
   - Load image and display original  
   - Generate caption using BLIP model
   - Display caption text in scrollable area
   - Save caption as text file

EVENT HANDLING:
- Mode change events with dynamic UI reconfiguration
- File browse events with validation and preview
- Process button events with background threading
- Save button events with file dialog integration

ERROR MANAGEMENT:
- Comprehensive error handling with user-friendly messages
- Input validation before processing
- Threading error handling with GUI feedback
- Graceful degradation for missing dependencies

PERFORMANCE FEATURES:
- Lazy model loading (models loaded only when first used)
- Background processing to prevent GUI freezing
- Memory management with explicit cleanup
- Progress feedback during long operations

FILE OPERATIONS:
- Support for multiple image formats (JPEG, PNG, BMP, TIFF, WebP)
- Image loading with format validation
- Save functionality for processed images and generated text
- Path management with user preference memory

INFORMATION DISPLAY:
- Real-time model information updates
- OOP concepts explanation for educational purposes
- Dynamic content based on current mode
- Scrollable text areas for detailed information

USER EXPERIENCE:
- Intuitive mode switching with automatic UI adaptation
- Clear visual feedback for all operations
- Disabled/enabled states for appropriate controls
- Responsive design with proper layout management

INTEGRATION POINTS:
- FileHandler integration for all file operations
- Logger integration for comprehensive activity tracking
- Custom widget integration for specialized displays
- Model integration through composition pattern

REFERENCES:
- ChatGPT-5: GUI design assistance and code structure optimization
- W3Schools Python OOP: https://www.w3schools.com/python/python_classes.asp
- Tkinter Documentation: https://docs.python.org/3/library/tkinter.html
- Real Python Tkinter Tutorial: https://realpython.com/python-gui-tkinter/
- Python Threading: https://docs.python.org/3/library/threading.html
================================================================================
"""

# main gui window for assignment 3

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any
import threading

from gui.widgets import ImageDisplayFrame, ScrollableInfoFrame
from gui.decorators import validate_input, log_operation, error_handler
from models.clothes_segmentation import ClothesSegmentationModel
from models.image_caption import ImageCaptionModel
from utils.file_handler import FileHandler
from utils.logger import logger


class ModelManager:
    # handles the ai models

    def __init__(self):
        # set up models lazily (only when we need them)
        # start in clothes segmentation mode by default
        self._clothes_segmentation_model: Optional[ClothesSegmentationModel] = None
        self._image_caption_model: Optional[ImageCaptionModel] = None
        self._model_cache: Dict[str, Any] = {}
        self._current_mode = "clothes_segmentation"
    
    @property
    def current_mode(self) -> str:
        # return current mode string
        return self._current_mode
    
    def _get_clothes_segmentation_model(self) -> ClothesSegmentationModel:
        # load clothes segmentation model only once
        if self._clothes_segmentation_model is None:
            logger.info("Initializing Clothes Segmentation (SegFormer) model")
            self._clothes_segmentation_model = ClothesSegmentationModel()
        return self._clothes_segmentation_model
    
    def _get_image_caption_model(self) -> ImageCaptionModel:
        # load image caption model only once
        if self._image_caption_model is None:
            logger.info("Initializing Image Caption model")
            self._image_caption_model = ImageCaptionModel()
        return self._image_caption_model
    
    @log_operation
    def process_clothes_segmentation(self, image: Image.Image) -> Image.Image:
        # run clothes segmentation and return overlay + colored map
        model = self._get_clothes_segmentation_model()
        return model.process({"image": image})  # returns (mask_img, colored_img)
    
    @log_operation
    def process_image_to_caption(self, image: Image.Image) -> str:
        # make a caption from image
        model = self._get_image_caption_model()
        return model.process(image)


class MainWindow(tk.Tk, ModelManager):
    # main window class (inherits from tkinter base + model manager)
    
    def __init__(self):
        # set up window + base classes
        tk.Tk.__init__(self)
        ModelManager.__init__(self)
        
        self._file_handler = FileHandler()
        self._selected_image_path: Optional[str] = None
        
        self.title("Assignment 3")
        self.state('zoomed')
        self.configure(bg='#f0f0f0')
        
        self._create_widgets()       # build widgets
        self._setup_layout()         # place them
        self._setup_event_handlers() # connect events
        self._on_mode_change()       # set initial mode state
        
        logger.log_user_action("Application started")
    
    def _create_widgets(self) -> None:
        # create gui widgets
        
        # title label
        self.title_label = tk.Label(
            self,
            text="Assignment 3 - AI Models",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        
        # mode selection
        self.mode_frame = tk.Frame(self, bg='#f0f0f0')
        self.mode_label = tk.Label(
            self.mode_frame,
            text="Select Mode:",
            font=('Arial', 12),
            bg='#f0f0f0'
        )
        self.mode_combo = ttk.Combobox(
            self.mode_frame,
            values=["Clothes Segmentation", "Image to Caption"],
            state="readonly",
            width=20
        )
        self.mode_combo.set("Clothes Segmentation")
        
        # main content frame
        self.content_frame = tk.Frame(self, bg='#f0f0f0')
        
        # input section
        self.input_frame = tk.LabelFrame(
            self.content_frame,
            text="Input",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        
        # no text prompt needed here (only used for caption mode later)
        self.text_input = None
        
        # image input widgets
        self.image_input_frame = tk.Frame(self.input_frame, bg='#f0f0f0')
        self.browse_button = tk.Button(
            self.image_input_frame,
            text="Browse Image...",
            font=('Arial', 10),
            command=self._browse_image
        )
        self.image_path_label = tk.Label(
            self.image_input_frame,
            text="No image selected",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#666666'
        )
        
        # process button
        self.process_button = tk.Button(
            self.input_frame,
            text="Segment Clothes",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self._process_input
        )
        
        # output section
        self.output_frame = tk.LabelFrame(
            self.content_frame,
            text="Output",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        
        # original image display (left side)
        self.original_image_frame = tk.LabelFrame(
            self.input_frame,
            text="Original Image",
            font=('Arial', 9, 'bold'),
            bg='#f0f0f0'
        )
        self.original_image_display = ImageDisplayFrame(self.original_image_frame, max_width=160, max_height=160)

        # segmentation displays (overlay + colored map)
        self.segmentation_overlay_label = tk.Label(
            self.output_frame,
            text="Overlay (Original + Clothes)",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        )
        # a bit smaller than input image for layout balance
        self.output_image_display = ImageDisplayFrame(self.output_frame, max_width=150, max_height=150)
        self.segmentation_colored_label = tk.Label(
            self.output_frame,
            text="Clothing Classes (Colored Map)",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        )
        self.segmentation_image_display = ImageDisplayFrame(self.output_frame, max_width=150, max_height=150)
        
        # text output (only shown in caption mode; not packed at start)
        self.text_output = tk.Text(
            self.output_frame,
            height=6,
            width=40,
            wrap=tk.WORD,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        
        # save buttons for segmentation outputs
        self.save_overlay_button = tk.Button(
            self.output_frame,
            text="Save Overlay",
            font=('Arial', 10),
            command=lambda: self._save_result(which="overlay"),
            state=tk.DISABLED
        )
        self.save_colored_button = tk.Button(
            self.output_frame,
            text="Save Colored",
            font=('Arial', 10),
            command=lambda: self._save_result(which="colored"),
            state=tk.DISABLED
        )
        # save button for caption mode only
        self.save_button = tk.Button(
            self.output_frame,
            text="Save Caption",
            font=('Arial', 10),
            command=self._save_result,
            state=tk.DISABLED
        )
        
        # info sections container
        self.info_container = tk.Frame(self, bg='#f0f0f0')
        
        # current model info section
        self.current_model_info = ScrollableInfoFrame(
            self.info_container,
            title="Current Model Information"
        )
        
        # oop concepts explanation section
        self.oop_concepts_info = ScrollableInfoFrame(
            self.info_container,
            title="OOP Concepts Demonstration"
        )
        
        # set initial information content
        self._setup_oop_concepts_info()
        self._update_current_model_info()
    
    def _setup_layout(self) -> None:
        # arrange + pack widgets
        
        # title
        self.title_label.pack(pady=10)
        
        # mode selection
        self.mode_frame.pack(fill=tk.X, padx=20, pady=5)
        self.mode_label.pack(side=tk.LEFT, padx=(0, 10))
        self.mode_combo.pack(side=tk.LEFT)
        
        # main content
        self.content_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # input (left) and output (right)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # input widgets
        self.image_input_frame.pack(pady=5)
        self.browse_button.pack()
        self.image_path_label.pack(pady=(5, 0))
        self.process_button.pack(pady=10)
        
        # output widgets (no text box packed here for segmentation mode)
        self.original_image_frame.pack(pady=5, fill=tk.X)
        self.original_image_display.pack()
        # pack segmentation visuals
        self.segmentation_overlay_label.pack(pady=(10,2))
        self.output_image_display.pack(pady=5)
        self.segmentation_colored_label.pack(pady=(10,2))
        self.segmentation_image_display.pack(pady=5)
        # segmentation save buttons
        self.save_overlay_button.pack(pady=5)
        self.save_colored_button.pack(pady=5)
        # caption save button added only in caption mode
        
        # info sections
        self.info_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 10))
        
        # pack info sections side by side
        self.current_model_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.oop_concepts_info.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    def _setup_event_handlers(self) -> None:
        # bind events
        self.mode_combo.bind('<<ComboboxSelected>>', lambda e: self._on_mode_change())
    
    def _on_mode_change(self) -> None:
        # handle mode change logic
        selected = self.mode_combo.get()
        
        if selected == "Clothes Segmentation":
            # segmentation mode
            self._current_mode = "clothes_segmentation"
            if not self.image_input_frame.winfo_ismapped():
                self.image_input_frame.pack(pady=5)
            self.process_button.config(text="Segment Clothes")
            # make sure segmentation widgets are visible
            self.segmentation_overlay_label.pack(pady=(10,2))
            self.output_image_display.pack(pady=5)
            self.segmentation_colored_label.pack(pady=(10,2))
            self.segmentation_image_display.pack(pady=5)
            if self.text_output.winfo_ismapped():
                self.text_output.pack_forget()
            # show segmentation save buttons; hide caption one
            self.save_overlay_button.pack(pady=5)
            self.save_colored_button.pack(pady=5)
            if self.save_button.winfo_ismapped():
                self.save_button.pack_forget()
            # disable segmentation save buttons until we process
            self.save_overlay_button.config(state=tk.DISABLED)
            self.save_colored_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            
        elif selected == "Image to Caption":
            # caption mode
            self._current_mode = "image_to_caption"
            if not self.image_input_frame.winfo_ismapped():
                self.image_input_frame.pack(pady=5)
            self.process_button.config(text="Generate Caption")
            # hide segmentation visuals, show text output
            if self.segmentation_overlay_label.winfo_ismapped():
                self.segmentation_overlay_label.pack_forget()
            if self.output_image_display.winfo_ismapped():
                self.output_image_display.pack_forget()
            if self.segmentation_colored_label.winfo_ismapped():
                self.segmentation_colored_label.pack_forget()
            if self.segmentation_image_display.winfo_ismapped():
                self.segmentation_image_display.pack_forget()
            if not self.text_output.winfo_ismapped():
                self.text_output.pack(pady=5)
            # show caption save button only
            if self.save_overlay_button.winfo_ismapped():
                self.save_overlay_button.pack_forget()
            if self.save_colored_button.winfo_ismapped():
                self.save_colored_button.pack_forget()
            if not self.save_button.winfo_ismapped():
                self.save_button.pack(pady=10)
            self.save_button.config(state=tk.DISABLED)
        
        # update model info
        self._update_current_model_info()
        # clear old output
        self._clear_output()
        
        logger.log_user_action(f"Mode changed to: {selected}")
    
    @error_handler("Failed to browse image")
    def _browse_image(self) -> None:
        # browse for image file
        try:
            image_path = self._file_handler.browse_image_file()
            if image_path:
                self._selected_image_path = str(image_path)
                filename = image_path.name
                self.image_path_label.config(text=filename, fg='#333333')
                # show image preview
                image = self._file_handler.load_image(image_path)
                # display original image
                self.original_image_display.display_image(image)
                # clear segmentation outputs
                self.output_image_display.clear_image()
                if hasattr(self, 'segmentation_image_display'):
                    self.segmentation_image_display.clear_image()
                # disable save buttons until we process again
                if hasattr(self, 'save_overlay_button'):
                    self.save_overlay_button.config(state=tk.DISABLED)
                if hasattr(self, 'save_colored_button'):
                    self.save_colored_button.config(state=tk.DISABLED)
                
                logger.log_user_action(f"Image selected: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    @validate_input
    @log_operation
    @error_handler("Processing failed")
    def _process_input(self) -> None:
        # process input in background thread to keep gui responsive
        # basic validation
        try:
            if self._current_mode == "clothes_segmentation":
                if not self._selected_image_path:
                    raise ValueError("Please select an image file for segmentation")
            elif self._current_mode == "image_to_caption":
                if not self._selected_image_path:
                    raise ValueError("Please select an image file")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        # start thread
        self._start_processing_thread()
    
    def _start_processing_thread(self) -> None:
        # start background processing thread
        self.process_button.config(state=tk.DISABLED, text="Processing...")
        self.save_button.config(state=tk.DISABLED)
        
        # create + start thread
        processing_thread = threading.Thread(target=self._process_in_background, daemon=True)
        processing_thread.start()
    
    def _process_in_background(self) -> None:
        # worker thread logic
        try:
            if self._current_mode == "clothes_segmentation":
                # need an image path
                if self._selected_image_path:
                    # load image
                    base_image = self._file_handler.load_image(Path(self._selected_image_path))
                else:
                    messagebox.showinfo("Select Image", "Please load an image to edit first.")
                    return
                overlay_img, colored_img = self.process_clothes_segmentation(base_image)
                # schedule gui update
                self.after(0, lambda o=overlay_img, c=colored_img: self._display_segmentation_result(o, c))
                
            elif self._current_mode == "image_to_caption":
                # load image
                image_path = Path(self._selected_image_path)
                
                image = self._file_handler.load_image(image_path)
                
                # generate caption
                caption = self.process_image_to_caption(image)
                
                # schedule gui update
                self.after(0, lambda: self._display_text_result(caption))
            
            # schedule final cleanup
            self.after(0, self._processing_complete)
            
        except Exception as e:
            # schedule error handling
            err_msg = str(e)
            self.after(0, lambda em=err_msg: self._processing_error(em))
    
    def _display_segmentation_result(self, overlay_img: Image.Image, colored_img: Image.Image) -> None:
        # show segmentation results
        self.output_image_display.display_image(overlay_img)
        self.segmentation_image_display.display_image(colored_img)
        # hide text box if visible
        if self.text_output.winfo_ismapped():
            self.text_output.pack_forget()
    
    def _display_text_result(self, caption: str) -> None:
        # show caption text
        self._set_text_output(caption)
    
    def _processing_complete(self) -> None:
        # reset ui when done
        # set button text based on mode
        if self._current_mode == "clothes_segmentation":
            self.process_button.config(state=tk.NORMAL, text="Segment Clothes")
        else:
            self.process_button.config(state=tk.NORMAL, text="Generate")
        if self._current_mode == "clothes_segmentation":
            # enable segmentation save buttons
            self.save_overlay_button.config(state=tk.NORMAL)
            self.save_colored_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.NORMAL)
    
    def _processing_error(self, error_msg: str) -> None:
        # show error and reset button label
        messagebox.showerror("Error", error_msg)
        if self._current_mode == "clothes_segmentation":
            self.process_button.config(state=tk.NORMAL, text="Segment Clothes")
        else:
            self.process_button.config(state=tk.NORMAL, text="Generate")
    
    @error_handler("Failed to save result")
    def _save_result(self, which: str = "caption") -> None:
        # save result (image or caption)
        try:
            if self._current_mode == "clothes_segmentation":
                if which == "overlay":
                    overlay_image = self.output_image_display.get_current_image()
                    if overlay_image:
                        overlay_path = self._file_handler.save_image(overlay_image, "clothes_overlay")
                        if overlay_path:
                            messagebox.showinfo("Success", f"Overlay saved: {overlay_path.name}")
                            logger.log_user_action(f"Overlay image saved: {overlay_path}")
                elif which == "colored":
                    colored_image = self.segmentation_image_display.get_current_image()
                    if colored_image:
                        colored_path = self._file_handler.save_image(colored_image, "clothes_colored")
                        if colored_path:
                            messagebox.showinfo("Success", f"Colored map saved: {colored_path.name}")
                            logger.log_user_action(f"Colored image saved: {colored_path}")
            
            elif self._current_mode == "image_to_caption":
                # Save caption text
                caption = self.text_output.get(1.0, tk.END).strip()
                if caption:
                    saved_path = self._file_handler.save_text(caption, "image_caption")
                    if saved_path:
                        messagebox.showinfo("Success", f"Caption saved to: {saved_path.name}")
                        logger.log_user_action(f"Caption saved: {saved_path}")
                        
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _clear_output(self) -> None:
        # clear output widgets
        self.output_image_display.clear_image()
        if hasattr(self, 'segmentation_image_display'):
            self.segmentation_image_display.clear_image()
        if hasattr(self, 'segmentation_overlay_label') and self._current_mode == "clothes_segmentation":
            # keep labels in segmentation mode
            pass
        self._set_text_output("")
        # disable save buttons
        if hasattr(self, 'save_overlay_button'):
            self.save_overlay_button.config(state=tk.DISABLED)
        if hasattr(self, 'save_colored_button'):
            self.save_colored_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
    
    def _set_text_output(self, text: str) -> None:
        # helper to set text box content
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)
        self.text_output.config(state=tk.DISABLED)
    

    
    def _update_current_model_info(self) -> None:
        # update model info box
        if self._current_mode == "clothes_segmentation":
            try:
                model = self._get_clothes_segmentation_model()
                info_dict = model.get_model_info()
                model_text = f"""Model Name: {info_dict.get('model_type', 'Clothes Segmentation (SegFormer)')}
Category: Image Segmentation
Description: {info_dict.get('description', 'Segments clothing items and colors them')}
Device: {info_dict.get('device', 'CPU')}"""
            except Exception:
                model_text = """Model Name: Clothes Segmentation (SegFormer)
Category: Image Segmentation
Description: Segments clothing items and colors them"""
        
        else:  # image_to_caption
            # Get model info from the actual model class
            try:
                model = self._get_image_caption_model()
                info_dict = model.get_model_info()
                model_text = f"""Model Name: {info_dict.get('model_type', 'BLIP Image Captioning')}
Category: Vision
Description: {info_dict.get('description', 'Generates captions for images')}
Device: {info_dict.get('device', 'CPU')}"""
            except Exception:
                model_text = """Model Name: BLIP Image Captioning
Category: Vision
Description: Generates descriptive captions for input images using BLIP transformer model"""
        
        self.current_model_info.set_content(model_text)
    
    def _setup_oop_concepts_info(self) -> None:
        # set oop concepts text
        oop_text = """OOP Concepts Used:

1. Multiple Inheritance:
MainWindow inherits from tk.Tk (GUI framework base) and ModelManager (model handling). It gets features from both.

2. Encapsulation:
Attributes like _clothes_segmentation_model and _image_caption_model are internal. Helper methods starting with an underscore are meant for internal use.

3. Polymorphism and Method Overriding:
Both AI model classes implement a process() method but they do different tasks. ClothesSegmentationModel performs image to image segmentation (clothing mask). ImageCaptionModel generates text from an image.

4. Multiple Decorators:
We stack decorators like @validate_input, @log_operation, and @error_handler to add reusable behaviors (input checking, logging, error handling) without changing core logic.

5. Abstraction:
The GUI just calls model.process(...) without needing to know how the underlying transformer models work internally.

Related Files:
- models/base_model.py (abstract base class)
- models/clothes_segmentation.py (clothes segmentation model)
- models/image_caption.py (captioning model)
- gui/main_window.py (GUI + coordination)"""
        
        self.oop_concepts_info.set_content(oop_text)