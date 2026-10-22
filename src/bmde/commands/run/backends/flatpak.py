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

import shutil
import subprocess

from bmde.core.exec import ExecOptions, run_cmd

from ..spec import RunSpecOpts
from .backend import RunBackend


class FlatpakRunner(RunBackend):
    def is_available(self) -> bool:
        return shutil.which("flatpak") is not None

    def run(self, spec: RunSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        # Adjust to your flatpak package and args
        args = ["flatpak", "run", "org.desmume.DeSmuME", str(spec.nds_rom)]
        return run_cmd(args, exec_opts)
