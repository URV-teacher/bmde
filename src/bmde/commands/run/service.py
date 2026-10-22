# bmde - Bare Metal Development Environment CLI
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from bmde.commands.run.backends.backend import RunBackend
from bmde.core import logging
from bmde.core.service import Service
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
