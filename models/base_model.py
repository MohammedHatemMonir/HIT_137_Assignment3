"""
================================================================================
BASE AI MODEL - ABSTRACT BASE CLASS
================================================================================

OVERVIEW:
This module defines the abstract base class (BaseAIModel) that serves as the 
foundation for all AI model implementations in the application. It establishes 
a common interface and shared functionality for AI model management, ensuring 
consistency across different model types while demonstrating key OOP principles.

KEY FUNCTIONALITY:
- Abstract base class using Python's ABC (Abstract Base Class) module
- Common model lifecycle management (loading, processing, unloading)
- Lazy loading pattern for efficient memory usage
- Performance monitoring with load time tracking
- Standardized model information interface

OOP CONCEPTS DEMONSTRATED:
1. ABSTRACTION: 
   - Abstract base class defining common interface
   - Abstract methods that must be implemented by subclasses
   - Encapsulation of common model properties and behaviors

2. TEMPLATE METHOD PATTERN:
   - _ensure_loaded() provides template for model initialization
   - Subclasses implement specific _load_model() details

3. ENCAPSULATION:
   - Private attributes (_model_name, _model, _is_loaded, _load_time)
   - Property decorators for controlled access to internal state
   - Protected methods for subclass use

DESIGN PATTERNS:
- Template Method: _ensure_loaded() calls abstract _load_model()
- Lazy Loading: Models only loaded when first accessed
- Strategy Pattern: Different processing strategies via subclasses

ABSTRACT METHODS (must be implemented by subclasses):
- _load_model(): Load the specific AI model and its dependencies
- process(): Execute the model's main functionality on input data

CONCRETE METHODS (inherited by all subclasses):
- model_name (property): Get the model identifier
- is_loaded (property): Check if model is loaded in memory
- load_time (property): Get the time taken to load the model
- _ensure_loaded(): Lazy loading mechanism with timing
- get_model_info(): Return standardized model information dictionary

USAGE PATTERN:
1. Subclass inherits from BaseAIModel
2. Implement abstract methods _load_model() and process()
3. Call _ensure_loaded() before processing to guarantee model availability
4. Use get_model_info() for runtime inspection and debugging

MEMORY MANAGEMENT:
- Models are only loaded when first needed (lazy loading)
- Load time is tracked for performance monitoring
- Boolean flag prevents redundant loading operations

SUBCLASS IMPLEMENTATIONS:
- ClothesSegmentationModel: SegFormer-based clothing segmentation
- ImageCaptionModel: BLIP-based image-to-text generation

REFERENCES:
- ChatGPT-5: Code optimization and documentation assistance
- W3Schools Python Classes: https://www.w3schools.com/python/python_classes.asp
- Python ABC Module Documentation: https://docs.python.org/3/library/abc.html
- Real Python Abstract Base Classes: https://realpython.com/python-interface/
================================================================================
"""

# base class for ai models

from abc import ABC, abstractmethod
from typing import Any, Optional
import time


class BaseAIModel(ABC):
    # abstract base for all model wrappers

    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None
        self._is_loaded = False
        self._load_time = None
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
    
    @property
    def load_time(self) -> Optional[float]:
        return self._load_time
    
    @abstractmethod
    def _load_model(self) -> None:
        # subclasses must load their specific model
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        # subclasses implement processing
        pass
    
    def _ensure_loaded(self) -> None:
        # lazy load on first use
        if not self._is_loaded:
            print(f"Loading {self._model_name}...")
            start_time = time.time()
            self._load_model()
            self._load_time = time.time() - start_time
            self._is_loaded = True
            print(f"Model loaded in {self._load_time:.2f} seconds")
    
    def get_model_info(self) -> dict:
        return {
            "name": self._model_name,
            "loaded": self._is_loaded,
            "load_time": self._load_time,
            "type": self.__class__.__name__
        }