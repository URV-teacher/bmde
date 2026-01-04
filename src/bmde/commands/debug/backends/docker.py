import subprocess

from bmde.core import logging
from bmde.core.docker import (
    can_run_docker,
    ensure_network_is_present,
    docker_remove_network,
)
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.types import DOCKER_DESMUME_DEBUG_NETWORK
from .backend import DebugBackend
from ..spec import DebugSpecOpts

log = logging.get_logger(__name__)


class DockerRunner(DebugBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(
        self, spec: DebugSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:

        docker_img = "aleixmt/insight:latest"
        mounts = [
            "-v",
            f"{spec.elf.parent}:/input:ro",
        ]
        envs = []
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
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        arguments: list[str] = []
        if spec.elf is not None:
            arguments += [f"/input/{spec.elf.name}"]

        if exec_opts.arguments is not None:
            arguments += list(exec_opts.arguments)

        docker_net = DOCKER_DESMUME_DEBUG_NETWORK
        if spec.docker_network is not None:
            docker_net = spec.docker_network
        network = ["--network", docker_net]

        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
            "-it",
            "--cap-add=SYS_PTRACE",
            "--security-opt",
            "seccomp=unconfined",
            *network,
            *mounts,
            *envs,
            *ports,
            *entry,
            docker_img,
            *arguments,
        ]

        ensure_network_is_present(docker_net)

        handle = run_cmd(run_args, exec_opts)

        if not exec_opts.background:
            docker_remove_network(docker_net)

        return handle
