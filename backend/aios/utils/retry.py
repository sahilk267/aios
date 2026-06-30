"""Retry utility with exponential backoff."""

import asyncio
import functools
import random
import structlog
from typing import Any, Callable, Optional, Type, Tuple

logger = structlog.get_logger(__name__)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """Decorator for retrying async or sync functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                   _attempts:
                        raise
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay,
                    )
                    if jitter:
                        delay += random.uniform(0, delay * 0.1)
                    logger.warning(
                        "Retrying after error",
                        function=func.__name__,
                        attempt=attempt,
                        delay=delay,
                        error=str(e),
                    )
                    if on_retry:
                        on_retry(attempt, e)
                    await asyncio.sleep(delay)
            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay,
                    )
                    if jitter:
                        delay += random.uniform(0, delay * 0.1)
                    logger.warning(
                        "Retrying after error",
                        function=func.__name__,
                        attempt=attempt,
                        delay=delay,
                        error=str(e),
                    )
                    if on_retry:
                        on_retry(attempt, e)
                    import time
                    time.sleep(delay)
            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
