"""
Retry Decorator for Resilient API Calls

WHY: External APIs can fail due to network issues, rate limits, or temporary outages.
Smart retry logic makes the system resilient without wasting resources on permanent failures.
"""

import time
import functools
from typing import Callable
import requests


def retry_on_error(max_attempts: int = 2, delay: float = 1.0):
    """
    Decorator to retry function calls on specific errors.
    
    WHY: Retry logic should be centralized and reusable across all tools.
    We only retry transient errors (timeout, rate limit, server error).
    
    Args:
        max_attempts: Maximum number of attempts (including first call)
        delay: Seconds to wait between retries
        
    Usage:
        @retry_on_error(max_attempts=2, delay=1.0)
        def my_api_call():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except requests.exceptions.Timeout as e:
                    # WHY: Timeout errors are transient, worth retrying
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay)
                        continue
                        
                except requests.exceptions.HTTPError as e:
                    # WHY: Only retry on rate limits (429) and server errors (5xx)
                    # Don't retry on client errors (4xx) as they won't succeed
                    if e.response is not None:
                        status_code = e.response.status_code
                        
                        # Retry on rate limit or server error
                        if status_code == 429 or status_code >= 500:
                            last_exception = e
                            if attempt < max_attempts:
                                time.sleep(delay)
                                continue
                    
                    # Don't retry on other HTTP errors (404, 400, etc.)
                    raise
                    
                except requests.exceptions.RequestException as e:
                    # WHY: Connection errors might be transient
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay)
                        continue
                        
                except Exception as e:
                    # WHY: Don't retry on non-network errors (validation, etc.)
                    raise
            
            # All attempts failed, raise the last exception
            raise last_exception
            
        return wrapper
    return decorator
