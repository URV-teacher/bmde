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

import subprocess
from pathlib import Path

from bmde.core import logging
from bmde.core.docker import can_run_docker, docker_image, docker_project_dir
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import host_uid_gid

from ..spec import BuildSpecOpts
from .backend import BuildBackend

log = logging.get_logger(__name__)

# Icon of libnds in the image: the default GAME_ICON of ds_rules, and the one set by the Makefile of the course
DEFAULT_ICON = "/URV/bmde/devkitPro/libnds/icon.bmp"


class DockerRunner(BuildBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: BuildSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        args = [
            "docker",
            "run",
            "--pull=always",  # Always update image to last version
            "--rm",
        ]  # Remove container after execution (one-off container)

        if exec_opts.interactive:
            args += ["-it"]  # Interactive mode with the container CLI

        if exec_opts.entrypoint:
            args += ["--entrypoint", str(exec_opts.entrypoint)]

        uid, gid = host_uid_gid()
        args += ["--user", f"{uid}:{gid}"]  # Make the generated files owned by the same user running the container

        project_dir = docker_project_dir(Path(spec.d))
        args += ["-v", f"{spec.d}:{project_dir}:rw"]
        args += ["-w", project_dir]  # Start with working directory in project mounted

        if spec.icon is not None:
            # Mounted over the default icon so that it is also used from another entrypoint (e.g. a shell)
            args += ["-v", f"{spec.icon}:{DEFAULT_ICON}:ro"]

        args += [docker_image("devkitarm-nds")]  # Base image

        if spec.icon is not None and exec_opts.entrypoint is None:
            # As in the host backend: a variable of the make command line also overrides a Makefile that chooses its
            # own icon, e.g. the template of devkitPro, which uses the icon.bmp of the project if there is one
            args += [f"GAME_ICON={DEFAULT_ICON}"]

        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)

        return run_cmd(args, exec_opts)
