# Decorators for the assignment

import functools
import time
from typing import Any, Callable, Dict


def validate_input(func: Callable) -> Callable:
    # Decorator to check if input is valid
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for empty string or None in first argument (typically user input)
        if len(args) > 1:
            user_input = args[1]  # args[0] is usually 'self'
            if not user_input or (isinstance(user_input, str) and user_input.strip() == ""):
                raise ValueError("Input cannot be empty")
        return func(*args, **kwargs)
    return wrapper


def log_operation(func: Callable) -> Callable:
    # Decorator to log function calls
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
    # Decorator to cache function results
    cache: Dict[str, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
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
    # Decorator to handle errors
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