# Base class for AI models

from abc import ABC, abstractmethod
from typing import Any, Optional
import time


class BaseAIModel(ABC):
    # Abstract base class for AI models
    
    def __init__(self, model_name: str):
        # Initialize model
        self._model_name = model_name  # Private attribute - encapsulation
        self._model = None  # Private model instance - lazy loading
        self._is_loaded = False  # Private state tracking
        self._load_time = None  # Private timing info
    
    @property
    def model_name(self) -> str:
        # Get model name
        return self._model_name
    
    @property
    def is_loaded(self) -> bool:
        # Check if model is loaded
        return self._is_loaded
    
    @property
    def load_time(self) -> Optional[float]:
        # Get model load time
        return self._load_time
    
    @abstractmethod
    def _load_model(self) -> None:
        # Load the model (must be implemented by subclasses)
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        # Process input (must be implemented by subclasses)
        pass
    
    def _ensure_loaded(self) -> None:
        # Make sure model is loaded
        if not self._is_loaded:
            print(f"Loading {self._model_name}...")
            start_time = time.time()
            self._load_model()
            self._load_time = time.time() - start_time
            self._is_loaded = True
            print(f"Model loaded in {self._load_time:.2f} seconds")
    
    def get_model_info(self) -> dict:
        # Get model information
        return {
            "name": self._model_name,
            "loaded": self._is_loaded,
            "load_time": self._load_time,
            "type": self.__class__.__name__
        }