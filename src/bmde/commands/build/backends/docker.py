import subprocess
from pathlib import Path

from bmde.core import logging
from bmde.core.docker import can_run_docker, docker_image, docker_project_dir
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import host_uid_gid

from ..spec import BuildSpecOpts
from .backend import BuildBackend

log = logging.get_logger(__name__)


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

        args += [docker_image("bmde-linux")]  # Base image

        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)

        return run_cmd(args, exec_opts)
