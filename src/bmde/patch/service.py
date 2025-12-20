from __future__ import annotations

from .backends.backend import PatchBackend
from .backends.docker import DockerRunner
from .backends.host import HostRunner
from .spec import PatchSpec
from ..core import logging
from ..core.exec import ExecOptions
from ..core.service import Service

log = logging.get_logger(__name__)


class PatchService(Service[PatchSpec, PatchBackend]):
    def __init__(self) -> None:
        super().__init__(["host", "docker"], {"host": HostRunner(), "docker": DockerRunner()})
