import os

from .backend import BuildBackend
from ..spec import BuildSpec
from bmde.core import logging
from bmde.core.docker import can_run_docker
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import host_uid_gid

log = logging.get_logger(__name__)


class DockerRunner(BuildBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: BuildSpec, exec_opts: ExecOptions) -> int:

        args = ["docker",
                    "run",
                    "--pull=always",  # Always update image to last version
                    "--rm",  # Remove container after execution (one-off container)
                    "-it"]  # Interactive mode with the container CLI

        if spec.entrypoint:
            args += ["--entrypoint", str(spec.entrypoint)]

        uid, gid = host_uid_gid()
        args += ["--user", f"{uid}:{gid}"]  # Make the generated files owned by the same user running the container

        project_path = os.path.basename(spec.d)
        args += ["-v", f"{spec.d}:/input/{project_path}:rw"]
        args += ["-w", f"/input/{project_path}"]  # Start with working directory in project mounted

        args += ["aleixmt/bmde-linux:latest"]  # Base image

        args += [*spec.arguments]

        return run_cmd(args, exec_opts)
