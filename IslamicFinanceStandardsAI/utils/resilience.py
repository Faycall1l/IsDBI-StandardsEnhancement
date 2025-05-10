"""
Resilience and Error Handling Module

This module provides robust error handling and resilience mechanisms for the
Islamic Finance Standards Enhancement system, ensuring graceful degradation
and recovery from various failure scenarios.
"""

import os
import time
import logging
import functools
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class ResilienceError(Exception):
    """Base class for resilience-related exceptions"""
    pass

class MaxRetriesExceededError(ResilienceError):
    """Exception raised when maximum retry attempts are exceeded"""
    pass

class CircuitBreakerOpenError(ResilienceError):
    """Exception raised when a circuit breaker is open"""
    pass

def retry(max_attempts: int = 3, 
          delay: float = 1.0, 
          backoff_factor: float = 2.0,
          exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception) -> Callable:
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        exceptions: Exception type(s) to catch and retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Max retry attempts ({max_attempts}) exceeded for {func.__name__}: {str(e)}")
                        raise MaxRetriesExceededError(f"Max retry attempts ({max_attempts}) exceeded: {str(e)}")
                    
                    logger.warning(f"Retry attempt {attempt}/{max_attempts} for {func.__name__} after error: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            # This should never be reached due to the exception above
            return None
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern implementation to prevent repeated calls to failing services
    """
    
    # Class-level circuit breaker registry
    _breakers = {}
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception):
        """
        Initialize a circuit breaker
        
        Args:
            name: Unique name for this circuit breaker
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Time in seconds before attempting to close the circuit
            exceptions: Exception type(s) to count as failures
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        if isinstance(exceptions, list):
            self.exceptions = tuple(exceptions)
        else:
            self.exceptions = (exceptions,)
        
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_time = None
        
        # Register this circuit breaker
        CircuitBreaker._breakers[name] = self
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func, *args, **kwargs):
        """Execute the function with circuit breaker protection"""
        if self.state == "OPEN":
            # Check if recovery timeout has elapsed
            if self.last_failure_time and (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                logger.info(f"Circuit {self.name} transitioning from OPEN to HALF-OPEN")
                self.state = "HALF-OPEN"
            else:
                logger.warning(f"Circuit {self.name} is OPEN, fast-failing call to {func.__name__}")
                raise CircuitBreakerOpenError(f"Circuit {self.name} is open")
        
        try:
            result = func(*args, **kwargs)
            
            # If we were in HALF-OPEN and the call succeeded, close the circuit
            if self.state == "HALF-OPEN":
                logger.info(f"Circuit {self.name} transitioning from HALF-OPEN to CLOSED")
                self.state = "CLOSED"
                self.failures = 0
            
            return result
            
        except self.exceptions as e:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.state == "CLOSED" and self.failures >= self.failure_threshold:
                logger.warning(f"Circuit {self.name} transitioning from CLOSED to OPEN after {self.failures} failures")
                self.state = "OPEN"
            
            # If we were in HALF-OPEN and the call failed, reopen the circuit
            if self.state == "HALF-OPEN":
                logger.warning(f"Circuit {self.name} transitioning from HALF-OPEN back to OPEN after failure")
                self.state = "OPEN"
            
            raise
    
    @classmethod
    def get(cls, name: str) -> Optional['CircuitBreaker']:
        """Get a registered circuit breaker by name"""
        return cls._breakers.get(name)
    
    @classmethod
    def reset(cls, name: str) -> bool:
        """Reset a circuit breaker to closed state"""
        if name in cls._breakers:
            breaker = cls._breakers[name]
            breaker.state = "CLOSED"
            breaker.failures = 0
            breaker.last_failure_time = None
            logger.info(f"Circuit {name} manually reset to CLOSED")
            return True
        return False

def fallback(fallback_function: Callable) -> Callable:
    """
    Fallback decorator to provide alternative behavior when a function fails
    
    Args:
        fallback_function: Function to call when the primary function fails
        
    Returns:
        Decorated function with fallback logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Function {func.__name__} failed with error: {str(e)}. Using fallback.")
                return fallback_function(*args, **kwargs)
        return wrapper
    return decorator

def timeout(seconds: int) -> Callable:
    """
    Timeout decorator to limit function execution time
    
    Args:
        seconds: Maximum execution time in seconds
        
    Returns:
        Decorated function with timeout logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set the timeout handler
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel the alarm
                signal.alarm(0)
            
            return result
        return wrapper
    return decorator

def capture_exception(func: Callable) -> Callable:
    """
    Exception capturing decorator that logs detailed exception information
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function with exception capturing
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log detailed exception information
            logger.error(f"Exception in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Re-raise the exception
            raise
    return wrapper

def health_check() -> Dict[str, Any]:
    """
    Perform a health check on all registered circuit breakers
    
    Returns:
        Dictionary with health status information
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "circuit_breakers": {}
    }
    
    for name, breaker in CircuitBreaker._breakers.items():
        breaker_status = {
            "state": breaker.state,
            "failures": breaker.failures,
            "last_failure_time": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None
        }
        
        health_status["circuit_breakers"][name] = breaker_status
        
        # If any circuit is open, the overall status is degraded
        if breaker.state == "OPEN":
            health_status["status"] = "degraded"
    
    return health_status
