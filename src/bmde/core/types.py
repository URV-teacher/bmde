"""
Helpers to parse strings & map log levels.
"""
from __future__ import annotations

import datetime
import pathlib
from enum import Enum
from typing import Iterable, List, Optional, Literal

import logging

log = logging.getLogger(__name__)  # Types cannot use logging module to avoid circular imports

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
        log.debug("Executing function parse from Backend")
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
    def parse(cls, value: Optional[str]) -> Optional[Backend]:
        return Backend.parse(value)


class DockerOutputName(str, Enum):
    """
    Execution environment backends. Obtained by composition with Backend class
    """
    VNC = "vnc"
    HOST = "host"

    @classmethod
    def parse(cls, value: Optional[str]) -> Optional[DockerOutputName]:
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

BackendName = Literal[Backend.HOST, Backend.DOCKER]
RunBackendName = Literal[RunBackend.HOST, RunBackend.DOCKER, RunBackend.FLATPAK]
# The possible backends that we have on the submodules
RunDockerOutputName = Literal[DockerOutputName.VNC, DockerOutputName.HOST]



