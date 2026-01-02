from __future__ import annotations

from bmde.core import logging
from bmde.core.service import Service
from .backends.backend import GitBackend
from .backends.docker import DockerRunner
from .backends.host import HostRunner
from .spec import GitSpecOpts
from ...core.types import BackendOptions

log = logging.get_logger(__name__)


class GitService(Service[GitSpecOpts, GitBackend]):
    def __init__(self) -> None:
        super().__init__(
            [BackendOptions.DOCKER, BackendOptions.HOST],
            {BackendOptions.HOST: HostRunner(), BackendOptions.DOCKER: DockerRunner()},
        )
