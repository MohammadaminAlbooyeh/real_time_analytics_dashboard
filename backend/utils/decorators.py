import functools
import time
import asyncio
from typing import Callable, Any
from backend.utils.logger import get_logger


def timed(func: Callable) -> Callable:
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed = time.time() - start
            get_logger("performance").info(f"{func.__name__} took {elapsed:.3f}s")

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.time() - start
            get_logger("performance").info(f"{func.__name__} took {elapsed:.3f}s")

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def retry(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
            raise last_exc

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2 ** attempt))
            raise last_exc

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
