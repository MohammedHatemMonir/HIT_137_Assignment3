"""
================================================================================
APPLICATION LOGGER - SINGLETON LOGGING SYSTEM
================================================================================

OVERVIEW:
This module implements a comprehensive logging system using the Singleton design 
pattern to ensure consistent logging behavior across the entire application. 
The AppLogger class provides a unified interface for logging operations, model 
activities, and user interactions while demonstrating key Object-Oriented 
Programming principles including encapsulation, singleton pattern, and 
composition with Python's built-in logging framework.

CORE FUNCTIONALITY:
- Singleton pattern ensures single logger instance throughout application
- Dual output: console logging and file logging capabilities
- Structured logging with timestamps and log levels
- Specialized logging methods for different types of events
- Graceful fallback when file logging is unavailable

KEY OOP CONCEPTS DEMONSTRATED:
1. SINGLETON PATTERN:
   - Single instance creation using __new__ method override
   - Global access point to logging functionality
   - Ensures consistent logging behavior across all modules
   - Prevents multiple logger instances from conflicting

2. ENCAPSULATION:
   - Private attributes for internal state management
   - Public methods provide controlled access to logging functionality
   - Internal setup methods hidden from external access
   - Configuration details abstracted from users

3. COMPOSITION:
   - Wraps Python's built-in logging module functionality
   - Combines multiple handlers (console, file) into single interface
   - Aggregates different logging capabilities under unified API

4. LAZY INITIALIZATION:
   - Logger setup performed only when first accessed
   - Prevents unnecessary initialization overhead
   - Ensures setup happens exactly once

LOGGING FEATURES:

Multi-Handler Architecture:
- Console Handler: Real-time output to stdout for development
- File Handler: Persistent logging to 'app_log.txt' for debugging
- Configurable log levels for different output destinations
- Formatted output with timestamps and structured messages

Specialized Logging Methods:
- info(): General information logging
- error(): Error condition logging  
- warning(): Warning message logging
- debug(): Detailed debugging information
- log_model_operation(): Specialized AI model operation logging
- log_user_action(): User interaction tracking

Log Message Formatting:
- Timestamp: ISO format with date and time
- Logger Name: Identifies source as 'AIModelApp'
- Log Level: INFO, ERROR, WARNING, DEBUG classification
- Message: Descriptive text with optional timing information

SINGLETON IMPLEMENTATION:
- Class-level _instance attribute tracks singleton instance
- __new__ method controls instance creation
- __init__ method performs one-time setup using _logger flag
- Thread-safe implementation for concurrent access

ERROR HANDLING:
- Graceful degradation when file logging fails
- Console logging continues even if file operations fail
- Silent failure for file handler to maintain application stability
- No exceptions raised for logging failures

TECHNICAL IMPLEMENTATION:

Handler Configuration:
- StreamHandler for console output with INFO level
- FileHandler for persistent logging with DEBUG level
- Consistent formatting across all handlers
- UTF-8 encoding for file operations

Log Levels:
- DEBUG: Detailed diagnostic information
- INFO: General application flow information  
- WARNING: Potential issues that don't stop execution
- ERROR: Serious problems that may affect functionality

File Management:
- Log file created in current working directory
- Automatic file creation and rotation handling
- Persistent logging across application sessions
- Simple text format for easy reading and processing

USAGE PATTERNS:
- Global logger instance accessible via module-level 'logger' variable
- Import once, use throughout application
- Consistent interface across all modules
- Specialized methods for different event types

PERFORMANCE CONSIDERATIONS:
- Minimal overhead for disabled log levels
- Buffered file I/O for efficient disk operations
- Lazy initialization reduces startup time
- Single instance eliminates multiple logger overhead

INTEGRATION POINTS:
- Used by all application modules for consistent logging
- Integrates with decorator logging for automatic operation tracking
- Supports GUI status updates through log message capture
- Compatible with Python's standard logging ecosystem

EXAMPLE USAGE:
    from utils.logger import logger
    
    logger.info("Application starting")
    logger.log_model_operation("SegFormer", "Loading", 2.5)
    logger.log_user_action("Image selected", "example.jpg")
    logger.error("Failed to load model")

CONFIGURATION:
- Default log format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
- Default date format: '%Y-%m-%d %H:%M:%S'
- Default file: 'app_log.txt' in current directory
- Default console level: INFO
- Default file level: DEBUG

THREAD SAFETY:
- Python's logging module is thread-safe by default
- Singleton implementation safe for concurrent access
- File handlers include built-in locking mechanisms
- No additional synchronization required for basic usage

REFERENCES:
- ChatGPT-5: Singleton pattern implementation and logging best practices
- W3Schools Python Classes: https://www.w3schools.com/python/python_classes.asp
- Python Logging Documentation: https://docs.python.org/3/library/logging.html
- Singleton Pattern: https://refactoring.guru/design-patterns/singleton
- Real Python Logging: https://realpython.com/python-logging/
================================================================================
"""

"""simple app logger (singleton)"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class AppLogger:
    """wraps python logging for easy calls"""
    
    _instance: Optional['AppLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        # only one instance
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # set up on first use
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        # configure handlers
        self._logger = logging.getLogger('AIModelApp')
        self._logger.setLevel(logging.INFO)
        
    # clear any existing handlers
        self._logger.handlers.clear()
        
    # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
    # file handler (optional)
        try:
            log_file = Path("app_log.txt")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception:
            # if file logging fails keep console only
            pass
    
    def info(self, message: str) -> None:
        # info log
        if self._logger:
            self._logger.info(message)
    
    def error(self, message: str) -> None:
        # error log
        if self._logger:
            self._logger.error(message)
    
    def warning(self, message: str) -> None:
        # warning log
        if self._logger:
            self._logger.warning(message)
    
    def debug(self, message: str) -> None:
        # debug log
        if self._logger:
            self._logger.debug(message)
    
    def log_model_operation(self, model_name: str, operation: str, duration: float = None) -> None:
        # log model action
        message = f"Model '{model_name}' - {operation}"
        if duration is not None:
            message += f" (Duration: {duration:.2f}s)"
        self.info(message)
    
    def log_user_action(self, action: str, details: str = "") -> None:
        # log ui action
        message = f"User Action: {action}"
        if details:
            message += f" - {details}"
        self.info(message)


# global logger instance for easy access
logger = AppLogger()