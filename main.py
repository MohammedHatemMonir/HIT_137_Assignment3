"""
================================================================================
AI MODEL DEMO APPLICATION - HIT137 ASSIGNMENT 3
================================================================================

OVERVIEW:
This is the main entry point for an AI Model Demo Application that showcases 
Object-Oriented Programming (OOP) concepts through practical implementation of 
AI models for computer vision tasks. The application provides a GUI interface 
for two primary functionalities:

1. CLOTHES SEGMENTATION: Uses SegFormer-based deep learning models to identify 
   and segment clothing items in images, producing colored overlay maps.

2. IMAGE CAPTIONING: Utilizes BLIP (Bootstrapping Language-Image Pre-training) 
   models to generate descriptive text captions from input images.

MAIN FEATURES:
- Tkinter-based graphical user interface with mode switching
- Real-time AI model processing with background threading
- Image loading, processing, and saving capabilities
- Comprehensive logging and error handling
- Modular architecture demonstrating advanced OOP principles

ARCHITECTURE OVERVIEW:
The application follows a modular design pattern with clear separation of concerns:

├── main.py (Entry point - dependency checking and application startup)
├── gui/
│   ├── main_window.py (Main GUI class with model management)
│   ├── widgets.py (Custom GUI components)
│   └── decorators.py (Function decorators for validation, logging, caching)
├── models/
│   ├── base_model.py (Abstract base class for AI models)
│   ├── clothes_segmentation.py (SegFormer-based clothing segmentation)
│   └── image_caption.py (BLIP-based image captioning)
└── utils/
    ├── logger.py (Singleton logging system)
    └── file_handler.py (File I/O operations)

OOP CONCEPTS DEMONSTRATED:
1. Inheritance: Multiple inheritance in MainWindow (tk.Tk + ModelManager)
2. Encapsulation: Private attributes and methods throughout codebase
3. Abstraction: BaseAIModel abstract class with common interface
4. Polymorphism: Different process() implementations in model subclasses
5. Composition: ModelManager composed within MainWindow
6. Singleton Pattern: Global logger instance
7. Decorator Pattern: Function decorators for cross-cutting concerns

DEPENDENCIES:
- torch (PyTorch for deep learning models)
- transformers (Hugging Face transformer models)
- Pillow (Image processing)
- tkinter (GUI framework - usually built-in with Python)
- numpy (Numerical operations)

USAGE:
Run this file directly to start the application:
    python main.py

The application will:
1. Check for required dependencies
2. Initialize the GUI interface
3. Load AI models on demand (lazy loading)
4. Provide interactive controls for image processing

ERROR HANDLING:
- Graceful dependency checking with informative error messages
- Exception handling with user-friendly error dialogs
- Comprehensive logging for debugging and monitoring

PERFORMANCE CONSIDERATIONS:
- Models are loaded lazily (only when first used)
- Background threading prevents GUI freezing during processing
- Memory management with model unloading capabilities
- CUDA acceleration when available

REFERENCES:
- ChatGPT-5: Code editing assistance and comment writing/spelling checks
- W3Schools Python OOP Tutorial: https://www.w3schools.com/python/python_classes.asp
- Real Python OOP Guide: https://realpython.com/python3-object-oriented-programming/
- Python Official Documentation: https://docs.python.org/3/tutorial/classes.html
================================================================================
"""

import sys
import traceback
from pathlib import Path

# Add project root to path so imports work when running directly
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def import_application_modules():
    """Try importing GUI components."""
    try:
        print("Loading GUI modules...")
        from gui.main_window import MainWindow
        from utils.logger import logger
        return MainWindow, logger
    except ImportError as e:
        print(f"Import Error in application modules: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error loading modules: {e}")
        traceback.print_exc()
        return None, None

# Try to import application modules
MainWindow, logger = import_application_modules()
if MainWindow is None:
    print("\nMake sure imports are installed")
    sys.exit(1)


def main():
    # Start the app
    try:
        # Create and start the GUI
        logger.info("Starting AI Model Demo Application")
        
        app = MainWindow()
        
        logger.info("GUI initialized successfully")
        
        # Run the app
        app.mainloop()
        
        logger.info("Application closed successfully")
        
    except Exception as e:
        # Handle any startup errors gracefully
        error_msg = f"Failed to start application: {str(e)}"
        logger.error(error_msg)
        print(f"ERROR: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Show error message
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Application Error", 
                f"Failed to start the application.\n\nError: {str(e)}\n\n"
                "Please ensure all dependencies are installed:\n"
                "pip install transformers diffusers torch Pillow"
            )
        except:
            pass
        
        sys.exit(1)


def check_dependencies():
    # Check if required packages are installed
    required_packages = [
        ('torch', 'PyTorch'),
        ('transformers', 'Hugging Face Transformers'),
        ('diffusers', 'Hugging Face Diffusers'),
        ('PIL', 'Pillow (PIL)'),
        ('tkinter', 'Tkinter (usually built-in)')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            logger.info(f"[OK] {description} available")
        except ImportError:
            missing_packages.append(description)
            logger.error(f"[MISSING] {description} not found")
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nTo install missing packages:")
        print("pip install transformers diffusers torch Pillow")
        return False
    
    return True


if __name__ == "__main__":
    # Run the app
    print("=" * 60)
    print("AI Model Demo Application - HIT137 Assignment 3")
    print("AI Model Demo Application - Assignment 3")
    print("Simple OOP + AI models demo")
    print("=" * 60)
    
    # Check dependencies before starting
    print("\nChecking dependencies...")
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        sys.exit(1)
    
    print("\nAll dependencies available. Starting application...\n")
    
    # Start the main application
    main()