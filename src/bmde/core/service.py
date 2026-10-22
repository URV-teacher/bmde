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

import subprocess
from abc import ABC
from subprocess import Popen
from typing import Any, Generic, TypeVar

from ..core import logging
from ..core.exec import ExecOptions
from .backend import Backend
from .spec import BaseSpec
from .types import BackendOptions

log = logging.get_logger(__name__)

SpecType = TypeVar("SpecType", bound=BaseSpec)  # will be GitSpec, BuildSpec, etc.
BackendType_co = TypeVar("BackendType_co", bound=Backend[Any], covariant=True)  # will be BuildBackend, RunBackend, etc.


class Service(Generic[SpecType, BackendType_co], ABC):
    def __init__(
        self,
        order: list[BackendOptions | BackendOptions],
        mapping: dict[BackendOptions | BackendOptions, BackendType_co],
    ) -> None:
        # We should use Any for a good generic class, but I prefer to break inheritance and restrict certain types
        # because I can not use a parent, since Enums are final (RunBackendOptions and BackendOptions
        self.order = order
        self.mapping = mapping

    def choose_backend(self, env: BackendOptions | BackendOptions | None) -> list[BackendType_co]:
        order = self.order
        if env:
            order = [env]  # force
        return [self.mapping[e] for e in order]

    def run(self, spec: SpecType, exec_opts: ExecOptions) -> int | Popen[bytes]:
        for backend in self.choose_backend(exec_opts.backend):
            if backend.is_available():
                ret = backend.run(spec, exec_opts)
                # Use isinstance for type narrowing
                if isinstance(ret, (int, subprocess.Popen)):
                    return ret
                    # returncode is guaranteed to be an int after communicate()
        raise RuntimeError("No suitable backend available")
