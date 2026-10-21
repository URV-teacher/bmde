"""
Helpers to parse strings & map log levels.
"""

from __future__ import annotations

import datetime
import logging
import pathlib
from enum import Enum

import platformdirs

log = logging.getLogger(__name__)  # Types cannot use logging module to avoid circular imports

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# Taken once, so every default log path of an execution points to the same file
NOW = datetime.datetime.now()
# The colons of DATE_FORMAT are not valid in Windows file names
LOG_FILE_DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"
APP_NAME = "bmde"
# Only used by run and debug modules in Docker mode
DOCKER_DESMUME_DEBUG_NETWORK = "bmde-debug"
# Name of the emulator container in debug mode, so the debugger can reach it through the Docker network
DOCKER_DESMUME_DEBUG_HOST = "desmume"


class BackendOptions(Enum):
    """
    Common environment backends.

    Note:
    - "bmde" is included for future/host-like flows (your Bare Metal Dev Env).
    """

    HOST = "host"
    DOCKER = "docker"
    FLATPAK = "flatpak"

    @classmethod
    def parse(cls, value: str | None) -> BackendOptions | None:
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


class DockerOutputOptions(Enum):
    """
    Execution environment backends. Obtained by composition with Backend class
    """

    VNC = "vnc"
    HOST = "host"
    NONE = "none"

    @classmethod
    def parse(cls, value: str | None) -> DockerOutputOptions | None:
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


class DebuggerOptions(Enum):
    """
    Debuggers that can be used by the debug command to connect to the emulator.
    """

    INSIGHT = "insight"
    GDB_MULTIARCH = "gdb-multiarch"


class LogLevel(Enum):
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
    def parse(cls, value: str | None) -> LogLevel | None:
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
    def get_default_log_level(cls) -> LogLevel:
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
    # The per-user log dir of the platform (~/.local/state/bmde/log on Linux) instead of the current directory, which
    # is usually the repository of a student and would end up with a logs/ folder in its commits
    return platformdirs.user_log_path(APP_NAME, appauthor=False) / f"{NOW.strftime(LOG_FILE_DATE_FORMAT)}.log"
