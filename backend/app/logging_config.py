from loguru import logger
import sys
from typing import Any, Dict


def configure_logging() -> None:
    """
    Configure application-wide structured logging using loguru.
    """
    # Force UTF-8 for Windows console to handle emojis
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "{extra[component]} - <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
    logger.add(
        "backend.log",
        level="DEBUG",
        encoding="utf-8",
        rotation="10 MB",
        enqueue=True
    )


def get_logger(component: str) -> "logger":
    """
    Get a logger with a bound component name for easier filtering.
    """
    return logger.bind(component=component)


def log_timing(
    log: "logger",
    event: str,
    timings_ms: Dict[str, float],
    extra: Dict[str, Any] | None = None,
) -> None:
    payload: Dict[str, Any] = {"event": event, "timings_ms": timings_ms}
    if extra:
        payload.update(extra)
    log.info(payload)

