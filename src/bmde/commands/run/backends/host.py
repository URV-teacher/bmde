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

from bmde.core import logging
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import is_command_available

from ..spec import RunSpecOpts
from .backend import RunBackend

log = logging.get_logger(__name__)


class HostRunner(RunBackend):
    def is_available(self) -> bool:
        return self.check()

    def check(self) -> bool:
        available = is_command_available("desmume") or is_command_available("desmume-cli")
        if not available:
            log.error("desmume or desmume-cli not found in PATH.")
        return available

    def run(self, spec: RunSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            desmume_path = shutil.which("desmume")
            desmumecli_path = shutil.which("desmume-cli")
            if desmume_path is not None:
                entry = desmume_path
            elif desmumecli_path is not None:
                entry = desmumecli_path
            else:
                entry = "desmume"
        args = [entry, str(spec.nds_rom)]
        if spec.fat_image:
            args += ["--cflash-image", str(spec.fat_image)]
        if spec.debug:
            # The option of DeSmuME 0.9.11, the version of the BMDE (newer versions have --arm9gdb-port and --gdb-stub)
            port = spec.arm9_debug_port if spec.arm9_debug_port is not None else 1024
            args += [f"--arm9gdb={port}"]
        if not spec.sound:
            args += ["--disable-sound"]
        if spec.controls:
            log.warning(f"Custom controls are only applied with the docker backend, ignoring {spec.controls}")
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
