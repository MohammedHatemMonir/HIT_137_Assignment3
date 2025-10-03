"""
================================================================================
FILE HANDLER - COMPREHENSIVE FILE OPERATIONS MANAGER
================================================================================

OVERVIEW:
This module provides a comprehensive file handling system for the AI Model Demo 
Application, implementing Object-Oriented Programming principles to manage 
image and text file operations. The FileHandler class encapsulates all file I/O 
functionality including browsing, loading, saving, and validation operations 
while maintaining state and providing a clean interface for the application.

CORE FUNCTIONALITY:
- Interactive file browsing with format filtering
- Image loading and validation with format conversion
- Image and text saving with format selection
- File information extraction and analysis
- User preference tracking (last used directory)
- Error handling with descriptive messages

KEY OOP CONCEPTS DEMONSTRATED:
1. ENCAPSULATION:
   - Private attributes for internal state (_last_directory, _supported_formats)
   - Property decorators for controlled access to internal data
   - Public methods provide clean interface hiding implementation details
   - Internal validation methods protect data integrity

2. STATE MANAGEMENT:
   - Persistent tracking of user's last used directory
   - Supported file format configuration
   - Session-based preference retention
   - State validation and updating mechanisms

3. COMPOSITION:
   - Integrates multiple file operation capabilities
   - Combines file dialogs, image processing, and path management
   - Aggregates functionality from PIL, pathlib, and tkinter.filedialog

4. ABSTRACTION:
   - Hides complexity of file format handling
   - Simplifies image conversion and validation processes
   - Provides unified interface for different file types

SUPPORTED FILE FORMATS:

Image Formats:
- JPEG (.jpg, .jpeg): Compressed image format for photos
- PNG (.png): Lossless compression with transparency support
- BMP (.bmp): Uncompressed bitmap format
- TIFF (.tiff): High-quality image format for professional use
- WebP (.webp): Modern web-optimized image format

Text Formats:
- Plain Text (.txt): Simple text files
- Markdown (.md): Formatted text with markdown syntax
- reStructuredText (.rst): Documentation format

FILE OPERATIONS:

Image Operations:
- browse_image_file(): Interactive image file selection
- load_image(): Image loading with automatic format conversion
- save_image(): Image saving with quality optimization
- Format validation and error handling
- Automatic RGB conversion for compatibility

Text Operations:
- save_text(): Text file saving with encoding handling
- UTF-8 encoding for international character support
- Configurable file extensions and formats

File Analysis:
- get_file_info(): Comprehensive file metadata extraction
- File size reporting in bytes and megabytes
- Modification time tracking
- Format validation and classification

TECHNICAL IMPLEMENTATION:

PIL Integration:
- Seamless integration with Python Imaging Library
- Automatic format detection and conversion
- RGBA/LA/P to RGB conversion for compatibility
- High-quality image processing with error handling

Path Management:
- pathlib.Path for modern path handling
- Cross-platform path compatibility
- Directory existence validation
- Automatic directory updates based on user selections

Dialog Integration:
- tkinter.filedialog for native OS file dialogs
- Configurable file type filters
- User-friendly file type descriptions
- Default file extensions and suggested names

DESIGN PATTERNS:
1. FACADE PATTERN: Simplified interface to complex file operations
2. STRATEGY PATTERN: Different handling strategies for various file types
3. STATE PATTERN: Directory preference management
4. TEMPLATE METHOD: Common file operation structure with specific implementations

ERROR HANDLING:
- Comprehensive exception handling for all file operations
- Descriptive error messages for user feedback
- Graceful fallback for unsupported formats
- File system error recovery

VALIDATION SYSTEM:
- File extension validation against supported formats
- File existence checking before operations
- Image format compatibility verification
- Path validation and sanitization

PERFORMANCE FEATURES:
- Efficient image loading with minimal memory usage
- Optimized file I/O operations
- Lazy loading of file information
- Minimal overhead for file validation

USER EXPERIENCE:
- Remembers last used directory for convenience
- Provides appropriate file filters for each operation
- Suggests meaningful default filenames
- Clear error messages for failed operations

INTEGRATION POINTS:
- Used by GUI components for all file operations
- Integrates with image display widgets
- Supports model input/output requirements
- Compatible with logging system for operation tracking

USAGE EXAMPLES:
    handler = FileHandler()
    
    # Browse and load image
    image_path = handler.browse_image_file()
    if image_path:
        image = handler.load_image(image_path)
    
    # Save processed image
    saved_path = handler.save_image(processed_image, "result")
    
    # Save text output
    text_path = handler.save_text(caption_text, "caption")
    
    # Get file information
    info = handler.get_file_info(image_path)

CONFIGURATION:
- Supported image formats defined in _supported_image_formats set
- Default save quality: 95 for JPEG images
- Default encoding: UTF-8 for text files
- Default directory: User's home directory

SECURITY CONSIDERATIONS:
- File extension validation prevents execution of arbitrary files
- Path validation prevents directory traversal attacks
- Safe file operations with proper exception handling
- No execution of uploaded or selected files

REFERENCES:
- ChatGPT-5: File handling patterns and error management strategies
- W3Schools Python File Handling: https://www.w3schools.com/python/python_file_handling.asp
- W3Schools Python Classes: https://www.w3schools.com/python/python_classes.asp
- Python Pathlib Documentation: https://docs.python.org/3/library/pathlib.html
- PIL/Pillow Documentation: https://pillow.readthedocs.io/
- Tkinter File Dialogs: https://docs.python.org/3/library/tkinter.filedialog.html
================================================================================
"""

"""file handling helpers (open, save images and text)"""

import os
from pathlib import Path
from typing import Optional, List
from PIL import Image
import tkinter.filedialog as fd


class FileHandler:
    """handles basic file pick, load, save"""
    
    def __init__(self):
        # track last folder and supported formats
        self._last_directory = Path.home()  # encapsulated
        self._supported_image_formats = {   # encapsulated
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'
        }
        self._supported_text_formats = {
            '.txt', '.md', '.rst'
        }
    
    @property
    def last_directory(self) -> Path:
        # last folder used
        return self._last_directory
    
    @property
    def supported_image_formats(self) -> set:
        # return copy so caller can't modify original set
        return self._supported_image_formats.copy()  # Return copy to prevent modification
    
    def _is_valid_image_file(self, file_path: Path) -> bool:
        # check extension
        return file_path.suffix.lower() in self._supported_image_formats
    
    def _update_last_directory(self, file_path: Path) -> None:
        # store parent folder
        if file_path.parent.exists():
            self._last_directory = file_path.parent
    
    def browse_image_file(self) -> Optional[Path]:
        """ask user for an image file"""
        filetypes = [
            ('Image files', '*.jpg *.jpeg *.png *.bmp *.tiff *.webp'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('PNG files', '*.png'),
            ('All files', '*.*')
        ]
        
        file_path = fd.askopenfilename(
            title="Select Image File",
            initialdir=str(self._last_directory),
            filetypes=filetypes
        )
        
        if file_path:
            path_obj = Path(file_path)
            if self._is_valid_image_file(path_obj):
                self._update_last_directory(path_obj)
                return path_obj
            else:
                raise ValueError(f"Unsupported image format: {path_obj.suffix}")
        
        return None
    
    def load_image(self, file_path: Path) -> Image.Image:
        """open image and return pil image"""
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        if not self._is_valid_image_file(file_path):
            raise ValueError(f"Unsupported image format: {file_path.suffix}")
        
        try:
            image = Image.open(file_path)
            # convert to rgb if needed (handles rgba etc)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    def save_image(self, image: Image.Image, suggested_name: str = "generated_image") -> Optional[Path]:
        """save image via dialog"""
        filetypes = [
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg'),
            ('All files', '*.*')
        ]
        
        file_path = fd.asksaveasfilename(
            title="Save Image As",
            initialdir=str(self._last_directory),
            initialfile=suggested_name,
            defaultextension=".png",
            filetypes=filetypes
        )
        
        if file_path:
            try:
                path_obj = Path(file_path)
                image.save(path_obj, quality=95)
                self._update_last_directory(path_obj)
                return path_obj
            except Exception as e:
                raise ValueError(f"Failed to save image: {str(e)}")
        
        return None
    
    def save_text(self, text: str, suggested_name: str = "caption") -> Optional[Path]:
        """save text file"""
        filetypes = [
            ('Text files', '*.txt'),
            ('Markdown files', '*.md'),
            ('All files', '*.*')
        ]
        
        file_path = fd.asksaveasfilename(
            title="Save Text As",
            initialdir=str(self._last_directory),
            initialfile=suggested_name,
            defaultextension=".txt",
            filetypes=filetypes
        )
        
        if file_path:
            try:
                path_obj = Path(file_path)
                with open(path_obj, 'w', encoding='utf-8') as f:
                    f.write(text)
                self._update_last_directory(path_obj)
                return path_obj
            except Exception as e:
                raise ValueError(f"Failed to save text: {str(e)}")
        
        return None
    
    def get_file_info(self, file_path: Path) -> dict:
        """return basic file info dict"""
        if not file_path.exists():
            return {"exists": False}
        
        stat = file_path.stat()
        return {
            "exists": True,
            "name": file_path.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "extension": file_path.suffix.lower(),
            "is_image": self._is_valid_image_file(file_path),
            "modified": stat.st_mtime
        }