from __future__ import annotations

from .backends.backend import BuildBackend
from .backends.docker import DockerRunner
from .backends.host import HostRunner
from .spec import BuildSpec
from bmde.core import logging
from bmde.core.service import Service

log = logging.get_logger(__name__)

class BuildService(Service[BuildSpec, BuildBackend]):
    def __init__(self) -> None:
        super().__init__(["host", "docker"], {"host": HostRunner(), "docker": DockerRunner()})
