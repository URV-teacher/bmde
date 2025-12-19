"""
Helpers to parse strings & map log levels.
"""
from __future__ import annotations

import datetime
import logging
import pathlib
from enum import Enum
from typing import Iterable, List, Optional, Literal

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
NOW = datetime.datetime.now().strftime(DATE_FORMAT)


class Backend(str, Enum):
    """
    Common environment backends.

    Note:
    - "bmde" is included for future/host-like flows (your Bare Metal Dev Env).
    """
    HOST = "host"
    DOCKER = "docker"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional["Backend"]:
        """Parse case-insensitively; returns None if value is falsy."""
        print("Executing function parse from Backend")
        if not value:
            return None
        norm = value.strip().lower()
        try:
            return cls(norm)  # Enum accepts the value directly
        except ValueError as exc:
            valid = ", ".join(v.value for v in cls)
            raise ValueError(f"Unknown environment '{value}'. Valid: {valid}") from exc



class RunBackend(str, Enum):
    """
    Execution environment backends. Obtained by composition with Backend class
    """
    HOST = Backend.HOST.value
    DOCKER = Backend.DOCKER.value
    FLATPAK = "flatpak"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional["Backend"]:
        return Backend.parse(value)


BackendName = Literal[Backend.HOST, Backend.DOCKER]
RunBackendName = Literal[RunBackend.HOST, RunBackend.DOCKER, RunBackend.FLATPAK]
# The possible backends that we have on the submodules
RunDockerOutputName = Literal["vnc", "host"]

# from here onward the code is not used

# Default backend priority when auto-selecting a runner for `bmde run`.
# host > docker > flatpak.
DEFAULT_RUN_ENV_PRIORITY: List[RunBackend] = [
    RunBackend.HOST,
    RunBackend.DOCKER,
    RunBackend.FLATPAK,
]

#: Reasonable default priority for build/patch flows (you can override per module).
DEFAULT_BUILD_ENV_PRIORITY: List[Backend] = [
    Backend.HOST,
    Backend.DOCKER
]


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

def choose_first_available(
    requested: Optional[Backend],
    candidates: Iterable[Backend],
    is_available: callable,
) -> Optional[Backend]:
    """
    Utility to pick the first available environment.

    - If `requested` is set, return it if available, else None.
    - Otherwise, return the first env in `candidates` for which `is_available(env)` is True.
    """
    print("Executed first available func in types.py")
    if requested:
        return requested if is_available(requested) else None
    for env in candidates:
        if is_available(env):
            return env
    return None



