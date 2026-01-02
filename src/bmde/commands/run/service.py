from __future__ import annotations


from bmde.core import logging
from bmde.core.service import Service
from bmde.commands.run.backends.backend import RunBackend
from bmde.core.types import BackendOptions as RunBackendName
from .backends.docker import DockerRunner
from .backends.flatpak import FlatpakRunner
from .backends.host import HostRunner
from .spec import RunSpecOpts

log = logging.get_logger(__name__)


class RunService(Service[RunSpecOpts, RunBackend]):
    def __init__(self) -> None:
        super().__init__(
            [RunBackendName.DOCKER, RunBackendName.FLATPAK, RunBackendName.HOST],
            {
                RunBackendName.HOST: HostRunner(),
                RunBackendName.DOCKER: DockerRunner(),
                RunBackendName.FLATPAK: FlatpakRunner(),
            },
        )
