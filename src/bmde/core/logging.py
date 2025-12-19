import datetime
import logging
import os.path
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler

from bmde.core.types import LogLevel, PROJECT_DIR, DATE_FORMAT

# ---- extend the logging module with TRACE
TRACE_LEVEL_NUM = 1
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
MESSAGE_FORMAT = "%(asctime)s | %(name)s | %(message)s"


def trace(self, message, *args, **kwargs):
    self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


def setup_logging(level: Optional[int | None], log_file: Optional[str | Path] = None) -> None:
    # Default level is INFO
    if level is None:
        level = logging.INFO

    logging.Logger.trace = trace

    handlers: list[logging.Handler] = []

    # ---- console (Rich)
    console = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=False,
        show_level=True,
        show_path=False,
    )
    common_formatter = logging.Formatter(MESSAGE_FORMAT, DATE_FORMAT)
    console.setLevel(level)
    console.setFormatter(common_formatter)
    handlers.append(console)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            path, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(common_formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,  # root captures everything
        handlers=handlers,
        format=MESSAGE_FORMAT,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a logger with trace() method available."""
    return logging.getLogger(name)
