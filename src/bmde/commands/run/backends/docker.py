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

from bmde.core import logging
from bmde.core.docker import (
    can_run_docker,
    docker_image,
    docker_remove_network,
    docker_screen_args,
    ensure_network_is_present,
    host_pulse_docker_args,
)
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.types import DOCKER_DESMUME_DEBUG_HOST, DockerOutputOptions

from ..spec import RunSpecOpts
from .backend import RunBackend

log = logging.get_logger(__name__)


class DockerRunner(RunBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: RunSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        docker_img = docker_image("desmume")
        mounts = [
            "-v",
            f"{spec.nds_rom.parent}:/roms:ro",
            "-v",
            "desmume_docker_config:/home/desmume/.config/desmume",
        ]
        img_opt = []
        debug_opt = []

        screen_mounts, envs, ports = docker_screen_args(spec.graphical_output)
        mounts += screen_mounts
        # Without a screen, the graphical emulator can't even start (it exits at once, "cannot open display"): run the
        # one of the command line instead, e.g. to run a ROM unattended
        if spec.graphical_output not in (DockerOutputOptions.HOST, DockerOutputOptions.VNC):
            envs += ["-e", "DESMUME_CLI=1"]

        if spec.debug:
            port = spec.arm9_debug_port if spec.arm9_debug_port is not None else 1024
            ports += ["-p", f"{port}:{port}"]  # Expose desmume to host on debug mode
            debug_opt = [f"--arm9gdb={port}"]

        if spec.fat_image:
            mounts += ["-v", f"{spec.fat_image}:/fs/fat.img:rw"]
            img_opt += ["--cflash-image", "/fs/fat.img"]

        if spec.controls:
            mounts += ["-v", f"{spec.controls}:/config/desmume.ini:ro"]

        if spec.sound:
            pulse_mounts, pulse_envs = host_pulse_docker_args()
            mounts += pulse_mounts
            envs += pulse_envs
        else:
            envs += ["-e", "DESMUME_USE_SOUND=0"]

        entry = []
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        arguments: list[str] = []
        if exec_opts.arguments is not None:
            arguments = list(exec_opts.arguments)

        arguments += [f"/roms/{spec.nds_rom.name}"]

        network_opt: list[str] = []
        if spec.debug:
            network_opt += [
                "--name",
                DOCKER_DESMUME_DEBUG_HOST,
                "--network",
                spec.docker_network,
            ]

        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
            "--init",  # Forwards signals to the entrypoint, so stopping the container stops the emulator
        ]

        if exec_opts.interactive:
            run_args += ["-it"]

        run_args += [
            *network_opt,
            *mounts,
            *envs,
            *ports,
            *entry,
            docker_img,
            *img_opt,
            *debug_opt,
            *arguments,
        ]

        docker_net = spec.docker_network if spec.debug else None

        if docker_net is not None and not exec_opts.dry_run:
            ensure_network_is_present(docker_net)

        handle = run_cmd(run_args, exec_opts)

        if docker_net is not None and not exec_opts.background and not exec_opts.dry_run:
            docker_remove_network(docker_net)

        return handle
