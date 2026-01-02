"""
Helpers to parse strings & map log levels.
"""

from __future__ import annotations

import datetime
import logging
import os
import pathlib
from enum import Enum
from typing import Optional

log = logging.getLogger(
    __name__
)  # Types cannot use logging module to avoid circular imports

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
NOW = datetime.datetime.now().strftime(DATE_FORMAT)
# Only used by run and debug modules in Docker mode
DOCKER_DESMUME_DEBUG_NETWORK = "bmde-debug"


class BackendOptions(str, Enum):
    """
    Common environment backends.

    Note:
    - "bmde" is included for future/host-like flows (your Bare Metal Dev Env).
    """

    HOST = "host"
    DOCKER = "docker"
    FLATPAK = "flatpak"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional["BackendOptions"]:
        """Parse case-insensitively; returns None if value is falsy."""
        log.debug("Executing function parse from Backend")
        if not value:
            return None
        norm = value.strip().lower()
        try:
            return cls(norm)  # Enum accepts the value directly
        except ValueError as exc:
            valid = ", ".join(v.value for v in cls)
            raise ValueError(f"Unknown environment '{value}'. Valid: {valid}") from exc


class DockerOutputOptions(str, Enum):
    """
    Execution environment backends. Obtained by composition with Backend class
    """

    VNC = "vnc"
    HOST = "host"
    NONE = "none"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional[DockerOutputOptions]:
        """Parse case-insensitively; returns None if value is falsy."""
        log.debug("Executing function parse from DockerOutputName")
        if not value:
            return None
        norm = value.strip().lower()
        try:
            return cls(norm)  # Enum accepts the value directly
        except ValueError as exc:
            valid = ", ".join(v.value for v in cls)
            raise ValueError(f"Unknown environment '{value}'. Valid: {valid}") from exc


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

    @classmethod
    def get_default_log_level(cls) -> "LogLevel":
        return LogLevel.INFO

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


def get_default_log_path() -> pathlib.Path:
    return pathlib.Path(str(os.path.join(".", "logs", "bmde", NOW + ".log")))
