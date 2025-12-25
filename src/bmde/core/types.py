"""
Helpers to parse strings & map log levels.
"""

from __future__ import annotations

import datetime
import logging
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


class RunBackendOptions(str, Enum):
    """
    Execution environment backends. Obtained by composition with Backend class
    """

    HOST = str(BackendOptions.HOST.value)
    DOCKER = str(BackendOptions.DOCKER.value)
    FLATPAK = "flatpak"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional[BackendOptions]:
        return BackendOptions.parse(value)


class DockerOutputOptions(str, Enum):
    """
    Execution environment backends. Obtained by composition with Backend class
    """

    VNC = "vnc"
    HOST = "host"

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
