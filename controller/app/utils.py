import logging
from asyncio import Lock
from functools import lru_cache
from functools import wraps

from rich.console import Console
from rich.logging import RichHandler

__all__ = ["get_logger", "async_lock"]

console = Console(color_system="256", width=150, style="blue")


@lru_cache()
def get_logger(module_name):
    from app.settings import Settings

    logger = logging.getLogger(module_name)
    handler = RichHandler(console=console, enable_link_path=False)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    settings = Settings()
    logger.setLevel(settings.log_level)
    return logger


def async_lock(func):
    lock = Lock()

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with lock:
            return await func(*args, **kwargs)

    return wrapper
