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

import os
import subprocess

from bmde.core import logging
from bmde.core.docker import can_run_docker, docker_image
from bmde.core.exec import ExecOptions, run_cmd

from ..spec import PatchSpecOpts
from .backend import PatchBackend

log = logging.get_logger(__name__)


class DockerRunner(PatchBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: PatchSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        entry = []
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        docker_img = docker_image("dlditool")

        mounts = [
            "-v",
            f"{spec.nds_rom.parent}:/input/{os.path.basename(spec.nds_rom.parent)}:rw",
        ]
        workdir_opt = [
            "-w",
            f"/input/{os.path.basename(spec.nds_rom.parent)}",
        ]  # Workdir

        arguments = []
        if exec_opts.arguments is not None:
            arguments = list(exec_opts.arguments)
        else:
            arguments = [
                "mpcf.dldi",
                f"/input/{os.path.basename(spec.nds_rom.parent)}/{os.path.basename(spec.nds_rom)}",
            ]

        run_args = ["docker", "run", "--pull=always", "--rm"]

        if exec_opts.interactive:
            run_args += ["-it"]

        run_args += [
            *mounts,
            *entry,
            *workdir_opt,
            docker_img,
            *arguments,
        ]

        log.debug("Patch arguments for Docker backend" + str(run_args))
        return run_cmd(run_args, exec_opts)
