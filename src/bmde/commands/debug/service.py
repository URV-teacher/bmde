from __future__ import annotations


from bmde.core import logging
from bmde.core.service import Service
from bmde.core.types import BackendOptions as RunBackendName
from .backends.backend import DebugBackend
from .backends.docker import DockerRunner
from .backends.host import HostRunner
from .spec import DebugSpecOpts

log = logging.get_logger(__name__)


class DebugService(Service[DebugSpecOpts, DebugBackend]):
    def __init__(self) -> None:
        super().__init__(
            [RunBackendName.HOST, RunBackendName.DOCKER],
            {
                RunBackendName.DOCKER: DockerRunner(),
                RunBackendName.HOST: HostRunner(),
            },
        )
