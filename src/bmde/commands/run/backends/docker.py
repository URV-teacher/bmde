import subprocess
from typing import List

from bmde.core import logging
from bmde.core.docker import (
    can_run_docker,
    ensure_network_is_present,
    docker_remove_network,
)
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.types import DOCKER_DESMUME_DEBUG_NETWORK
from .backend import RunBackend
from ..spec import RunSpecOpts

log = logging.get_logger(__name__)


class DockerRunner(RunBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(
        self, spec: RunSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        docker_img = "aleixmt/desmume:latest"
        mounts = [
            "-v",
            f"{spec.nds_rom.parent}:/roms:ro",
            "-v",
            "desmume_docker_config:/home/desmume/.config/desmume",
        ]
        envs = (
            []
        )  # TODO: Balance logic with desmume docker entrypoint ["-e", f"ROM=/roms/{spec.nds.name}"]
        ports = []
        img_opt = []
        if spec.fat_image:
            mounts += ["-v", f"{spec.fat_image}:/fs/fat.img:rw"]
            img_opt += ["--cflash-image", "/fs/fat.img"]

        if spec.graphical_output == "host":
            mounts += ["-v", "/tmp/.X11-unix:/tmp/.X11-unix"]
            envs += [
                "-e",
                "MODE=host",
                "-e",
                "DISPLAY=:0",
                "-e",
                "XVFB_DISPLAY=:99",
                "-e",
                "GEOMETRY=1024x768x24",
                "-e",
                "VNC_PORT=5900",
            ]
        if spec.graphical_output == "vnc":
            ports += ["-p", "3000:3000", "-p", "3001:3001"]
            envs += ["-e", "MODE=vnc", "-e", "DISPLAY=:0"]
        entry = []
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        debug_opt = []
        print("startingdebug block. debug is: " + str(spec.debug))
        if spec.debug:
            print("spec debug")
            if spec.arm9_debug_port is not None:
                debug_opt = [f"--arm9gdb-port={str(spec.arm9_debug_port)}"]
            else:
                debug_opt = ["--arm9gdb-port=1000"]

        arguments: list[str] = []
        if exec_opts.arguments is not None:
            arguments = List(exec_opts.arguments)

        if spec.nds_rom is not None:
            envs += ["-e", f"ROM=/roms/{spec.nds_rom.name}"]

        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
            "-it",
            "--name",
            "desmume",
            "--network",
            "bmde-debug",
            *mounts,
            *envs,
            *ports,
            *entry,
            docker_img,
            *img_opt,
            *debug_opt,
            *arguments,
        ]

        docker_net = None
        if spec.debug:
            docker_net = DOCKER_DESMUME_DEBUG_NETWORK
            if spec.docker_network is not None:
                docker_net = spec.docker_network

        if docker_net is not None:
            ensure_network_is_present(docker_net)

        handle = run_cmd(run_args, exec_opts)

        if docker_net is not None and not exec_opts.background:
            docker_remove_network(DOCKER_DESMUME_DEBUG_NETWORK)

        return handle
