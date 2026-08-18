import asyncio
import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger("pimpulse.reliability")

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    backoff_factor: float = 2.0,
    retry_exceptions: tuple = (Exception,)
):
    """
    Decorator for async/sync functions with exponential backoff on transient failures.
    Non-retryable 4xx client errors or explicit valuation errors will raise immediately.
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                attempt = 0
                while attempt < max_attempts:
                    try:
                        return await func(*args, **kwargs)
                    except retry_exceptions as e:
                        err_str = str(e).lower()
                        # Fast fail on non-retryable 401/403/400 (auth/bad request)
                        if "401" in err_str or "unauthorized" in err_str or "invalid api key" in err_str:
                            logger.error(f"[RELIABILITY] Non-retryable error in {func.__name__}: {e}")
                            raise e
                        
                        attempt += 1
                        if attempt >= max_attempts:
                            logger.error(f"[RELIABILITY] Max retry attempts ({max_attempts}) exceeded in {func.__name__}: {e}")
                            raise e
                        
                        delay = base_delay * (backoff_factor ** (attempt - 1))
                        logger.warning(f"[RELIABILITY] Retryable error in {func.__name__} (attempt {attempt}/{max_attempts}). Retrying in {delay:.2f}s: {e}")
                        await asyncio.sleep(delay)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                attempt = 0
                while attempt < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except retry_exceptions as e:
                        err_str = str(e).lower()
                        if "401" in err_str or "unauthorized" in err_str or "invalid api key" in err_str:
                            logger.error(f"[RELIABILITY] Non-retryable error in {func.__name__}: {e}")
                            raise e
                        
                        attempt += 1
                        if attempt >= max_attempts:
                            logger.error(f"[RELIABILITY] Max retry attempts ({max_attempts}) exceeded in {func.__name__}: {e}")
                            raise e
                        
                        delay = base_delay * (backoff_factor ** (attempt - 1))
                        logger.warning(f"[RELIABILITY] Retryable error in {func.__name__} (attempt {attempt}/{max_attempts}). Retrying in {delay:.2f}s: {e}")
                        time.sleep(delay)
            return sync_wrapper
    return decorator
