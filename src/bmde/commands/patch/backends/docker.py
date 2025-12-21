import os
import subprocess

from .backend import PatchBackend
from ..spec import PatchSpec
from bmde.core import logging
from bmde.core.docker import can_run_docker
from bmde.core.exec import run_cmd, ExecOptions

log = logging.get_logger(__name__)

class DockerRunner(PatchBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(self, spec: PatchSpec, exec_opts: ExecOptions) -> int:
        entry = []
        if spec.entrypoint:
            entry = ["--entrypoint", str(spec.entrypoint)]

        docker_img = "aleixmt/dlditool:latest"

        dirname = os.path.basename(spec.d)
        mounts = ["-v", f"{spec.d}:/input/{dirname}:rw"]
        envs = []
        ports = []
        workdir_opt = ["-w", f"/input/{dirname}"]  # Workdir

        run_args = ["docker", "run", "--pull=always", "--rm", "-it", *mounts, *envs, *ports, *entry, *workdir_opt, docker_img,
                    *spec.arguments]

        log.debug("Patch arguments for Docker backend" + str(run_args))
        return run_cmd(run_args, exec_opts)
