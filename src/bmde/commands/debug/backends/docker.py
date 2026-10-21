import subprocess
import sys

from bmde.core import logging
from bmde.core.docker import can_run_docker, docker_image, docker_project_dir, docker_screen_args
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.types import DOCKER_DESMUME_DEBUG_HOST, BackendOptions

from ..spec import DebugSpecOpts
from .backend import DebugBackend

log = logging.get_logger(__name__)

# Host port of the VNC server of the debugger, next to the one of the emulator
DEBUGGER_VNC_HOST_PORT = 5901


class DockerRunner(DebugBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: DebugSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        docker_img = docker_image("insight")
        project_dir = docker_project_dir(spec.elf.parent)
        mounts = [
            "-v",
            f"{spec.elf.parent}:{project_dir}:ro",
            "-v",
            "insight_docker_config:/home/insight",  # Keeps the preferences, sessions and breakpoints of Insight
        ]

        screen_mounts, envs, ports = docker_screen_args(spec.docker_screen, vnc_host_port=DEBUGGER_VNC_HOST_PORT)
        mounts += screen_mounts

        # Reach the GDB stub of the emulator through the Docker network if it runs in a container, or through the host
        emulator = spec.RunSpec
        port = emulator.RunSpecOpts.arm9_debug_port if emulator.RunSpecOpts.arm9_debug_port is not None else 1024
        if emulator.SpecExecOpts.backend == BackendOptions.DOCKER:
            network = ["--network", emulator.RunSpecOpts.docker_network]
            target = f"{DOCKER_DESMUME_DEBUG_HOST}:{port}"
        else:
            network = ["--add-host", "host.docker.internal:host-gateway"]
            target = f"host.docker.internal:{port}"
        envs += ["-e", f"DEBUGGER={spec.debugger.value}", "-e", f"GDB_TARGET={target}"]

        entry = []
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        arguments = [spec.elf.name]
        if exec_opts.arguments is not None:
            arguments += list(exec_opts.arguments)

        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
            # Terminal debuggers need a TTY, only available if bmde has one
            "-it" if sys.stdin.isatty() else "-i",
            *network,
            *mounts,
            # Same working directory as the build, so the debugger finds the sources of the ELF
            "-w",
            project_dir,
            *envs,
            *ports,
            *entry,
            docker_img,
            *arguments,
        ]

        return run_cmd(run_args, exec_opts)
