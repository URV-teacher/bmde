import logging
import os.path
from enum import Enum
from pathlib import Path
from typing import Optional, LiteralString, Literal

from rich.logging import RichHandler

from bmde.core.types import PROJECT_DIR, DATE_FORMAT, NOW

# ---- extend the logging module with TRACE
TRACE_LEVEL_NUM = 1
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
MESSAGE_FORMAT = "%(asctime)s | %(name)s | %(message)s"

def get_default_log_path() -> LiteralString | str | bytes:
    return os.path.join(PROJECT_DIR, "logs", NOW + ".log")


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


class LogLevel(str, Enum):
    """
    Logical log levels for the CLI.

    Includes a custom TRACE (more verbose than DEBUG) and QUIET
    (suppresses all output beyond CRITICAL).
    """
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUIET = "quiet"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional["LogLevel"]:
        """Parse case-insensitively; returns None if value is falsy."""
        print("Executing function parse from LogLevel")
        if not value:
            return None
        norm = value.strip().lower()
        try:
            return cls(norm)
        except ValueError as exc:
            valid = ", ".join(v.value for v in cls)
            raise ValueError(f"Unknown log level '{value}'. Valid: {valid}") from exc

    def to_logging_level(self) -> int:
        if self is LogLevel.TRACE:
            return 0
        if self is LogLevel.DEBUG:
            return logging.DEBUG
        if self is LogLevel.INFO:
            return logging.INFO
        if self is LogLevel.WARNING:
            return logging.WARNING
        if self is LogLevel.ERROR:
            return logging.ERROR
        if self is LogLevel.QUIET:
            return logging.CRITICAL + 10
        # Fallback
        return logging.INFO

LogLevelLiteral = Literal.__getitem__(tuple(v.value for v in LogLevel))



