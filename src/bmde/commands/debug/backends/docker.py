import subprocess
from typing import List

from bmde.core import logging
from bmde.core.docker import can_run_docker
from bmde.core.exec import run_cmd, ExecOptions
from .backend import DebugBackend
from ..spec import DebugSpec

log = logging.get_logger(__name__)


class DockerRunner(DebugBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(
        self, spec: DebugSpec, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:

        docker_img = "aleixmt/insight:latest"
        mounts = [
            "-v",
            f"{spec.elf.parent}:/roms:ro",
        ]
        envs = ["-e", f"ROM=/roms/{spec.elf.name}"]
        ports = []

        if spec.docker_screen == "host":
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
        if spec.docker_screen == "vnc":
            ports += ["-p", "3000:3000", "-p", "3001:3001"]
            envs += ["-e", "MODE=vnc", "-e", "DISPLAY=:0"]
        entry = []
        if spec.entrypoint:
            entry = ["--entrypoint", str(spec.entrypoint)]

        arguments: list[str] = []
        if spec.arguments is not None:
            arguments = List(spec.arguments)
        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
            "-it",
            "--name",
            "insight",
            "--network",
            "bmde-debug",
            *mounts,
            *envs,
            *ports,
            *entry,
            docker_img,
            *arguments,
        ]

        return run_cmd(run_args, exec_opts)
