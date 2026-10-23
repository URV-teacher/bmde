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
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from bmde.core.exec import ExecOptions
from bmde.core.spec import BaseSpec

SpecType = TypeVar("SpecType", bound=BaseSpec)  # will be GitSpec, BuildSpec, etc.


class Backend(ABC, Generic[SpecType]):
    """Generic interface for backends.

    Each runner backend must implement a function to use it and to determine if it is available.
    """

    @abstractmethod
    def is_available(self) -> bool: ...

    def check(self) -> bool:
        """Performs detailed checks to verify if the backend is correctly configured.

        Returns True if all checks pass, False otherwise.
        Default implementation returns True.
        """
        return True

    @abstractmethod
    def run(self, spec: SpecType, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]: ...
