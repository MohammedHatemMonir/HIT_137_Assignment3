"""
================================================================================
FUNCTION DECORATORS - CROSS-CUTTING CONCERNS IMPLEMENTATION
================================================================================

OVERVIEW:
This module implements a collection of function decorators that demonstrate 
the Decorator Pattern in Object-Oriented Programming. These decorators provide 
cross-cutting concerns such as input validation, operation logging, result 
caching, and error handling. They can be applied to any function to add 
behavior without modifying the original function code, showcasing the power 
of composition over inheritance.

DECORATORS PROVIDED:
1. @validate_input: Input validation and sanitization
2. @log_operation: Automatic operation timing and logging
3. @cache_result: Simple result caching mechanism  
4. @error_handler: Graceful error handling with custom messages

KEY OOP CONCEPTS DEMONSTRATED:
1. DECORATOR PATTERN:
   - Wraps existing functions with additional behavior
   - Maintains original function signature and semantics
   - Allows multiple decorators to be stacked on single function
   - Provides separation of concerns

2. HIGHER-ORDER FUNCTIONS:
   - Functions that take other functions as parameters
   - Functions that return functions (closures)
   - Dynamic behavior modification at runtime

3. COMPOSITION OVER INHERITANCE:
   - Adding functionality through composition rather than class inheritance
   - Flexible behavior modification without changing class hierarchies
   - Runtime behavior enhancement

4. ASPECT-ORIENTED PROGRAMMING:
   - Cross-cutting concerns implemented as reusable aspects
   - Separation of business logic from infrastructure concerns
   - Consistent behavior across multiple functions

DECORATOR DETAILS:

@validate_input:
- PURPOSE: Ensures function inputs meet basic validation criteria
- FUNCTIONALITY:
  * Checks for empty or None inputs in first argument
  * Validates string inputs are not blank/whitespace-only
  * Raises ValueError for invalid inputs with descriptive messages
- USAGE: Applied to functions that require non-empty user inputs
- OOP CONCEPT: Input validation as cross-cutting concern

@log_operation:
- PURPOSE: Automatic logging of function execution with timing
- FUNCTIONALITY:
  * Logs function start time with timestamp
  * Measures and reports execution duration
  * Logs successful completion or failure details
  * Provides performance monitoring capabilities
- USAGE: Applied to time-critical operations and AI model processing
- OOP CONCEPT: Logging as aspect-oriented concern

@cache_result:
- PURPOSE: Simple result caching to avoid redundant computations
- FUNCTIONALITY:
  * Generates cache keys from function arguments
  * Stores function results in memory cache
  * Returns cached results for repeated calls with same arguments
  * Provides cache hit/miss logging
- USAGE: Applied to expensive operations with deterministic results
- OOP CONCEPT: Caching as performance enhancement aspect
- LIMITATIONS: Simple hash-based caching, not production-ready

@error_handler:
- PURPOSE: Graceful error handling with custom error messages
- FUNCTIONALITY:
  * Catches all exceptions from decorated functions
  * Logs errors with custom messages
  * Returns None instead of propagating exceptions
  * Prevents application crashes from individual function failures
- USAGE: Applied to functions where failures should not crash the application
- OOP CONCEPT: Error handling as defensive programming aspect

TECHNICAL IMPLEMENTATION:

Decorator Architecture:
- Uses functools.wraps to preserve function metadata
- Implements closure pattern for state preservation
- Maintains original function signatures for transparency
- Supports both positional and keyword arguments

Caching Mechanism:
- Dictionary-based cache with string keys
- Hash-based key generation from arguments
- Module-level cache storage (persistent across calls)
- Simple but effective for demonstration purposes

Logging Integration:
- Integrates with application logging system
- Provides structured log messages
- Includes timing information for performance analysis
- Supports different log levels for various scenarios

Error Handling Strategy:
- Fail-safe approach (return None instead of crashing)
- Comprehensive error logging for debugging
- Maintains application stability
- Allows graceful degradation of functionality

DESIGN PATTERNS:
1. DECORATOR PATTERN: Core pattern for adding behavior
2. TEMPLATE METHOD: Common structure across all decorators
3. STRATEGY PATTERN: Different validation/handling strategies
4. FACADE PATTERN: Simplified interface to complex functionality

USAGE EXAMPLES:
    @validate_input
    @log_operation 
    @error_handler("Failed to process image")
    def process_image(self, image_data):
        # Function implementation
        pass

    @cache_result
    @log_operation
    def expensive_computation(self, data):
        # Expensive operation that benefits from caching
        pass

STACKING DECORATORS:
- Multiple decorators can be applied to single function
- Execution order is bottom-up (innermost decorator runs first)
- Each decorator wraps the result of the previous decorator
- Allows for complex behavior composition

PERFORMANCE CONSIDERATIONS:
- Minimal overhead for simple decorators
- Caching decorator trades memory for computation time
- Logging decorator adds small timing overhead
- Error handling decorator has negligible performance impact

LIMITATIONS:
- Simple caching implementation not suitable for production
- Hash-based cache keys may have collision issues
- Error handler always returns None (not configurable)
- No cache size limits or expiration policies

FUTURE ENHANCEMENTS:
- Configurable cache policies (size limits, TTL)
- More sophisticated validation rules
- Conditional logging based on log levels
- Customizable error return values

REFERENCES:
- ChatGPT-5: Decorator pattern implementation and best practices
- W3Schools Python Decorators: https://www.w3schools.com/python/python_functions.asp
- Real Python Decorators: https://realpython.com/primer-on-python-decorators/
- Python Functools Documentation: https://docs.python.org/3/library/functools.html
- Decorator Pattern: https://refactoring.guru/design-patterns/decorator
================================================================================
"""

"""simple decorators used in the app"""

import functools
import time
from typing import Any, Callable, Dict


def validate_input(func: Callable) -> Callable:
    # check first arg (user input) not empty
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # look for empty or blank input in first real arg
        if len(args) > 1:
            user_input = args[1]  # args[0] is usually 'self'
            if not user_input or (isinstance(user_input, str) and user_input.strip() == ""):
                raise ValueError("Input cannot be empty")
        return func(*args, **kwargs)
    return wrapper


def log_operation(func: Callable) -> Callable:
    # log time taken
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"[LOG] Starting {func.__name__} at {time.strftime('%H:%M:%S')}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"[LOG] {func.__name__} completed in {end_time - start_time:.2f}s")
            return result
        except Exception as e:
            print(f"[LOG] {func.__name__} failed: {str(e)}")
            raise
    return wrapper


def cache_result(func: Callable) -> Callable:
    # very basic cache using hash of args
    cache: Dict[str, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # build cache key
        cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
        
        if cache_key in cache:
            print(f"[CACHE] Returning cached result for {func.__name__}")
            return cache[cache_key]
        
        result = func(*args, **kwargs)
        cache[cache_key] = result
        print(f"[CACHE] Cached result for {func.__name__}")
        return result
    
    return wrapper


def error_handler(error_message: str = "An error occurred"):
    # catch errors and return none instead of crashing
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[ERROR] {error_message}: {str(e)}")
                # Return None or appropriate default value instead of crashing
                return None
        return wrapper
    return decorator