import os

from bmde.core import logging
from bmde.core.docker import can_run_docker
from bmde.core.exec import run_cmd, ExecOptions
from .backend import PatchBackend
from ..spec import PatchSpec

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
        workdir_opt = ["-w", f"/input/{dirname}"]  # Workdir

        arguments = []
        if spec.arguments is not None:
            arguments = list(spec.arguments)

        run_args = ["docker", "run", "--pull=always", "--rm", "-it", *mounts, *entry, *workdir_opt, docker_img,
                    *arguments]

        log.debug("Patch arguments for Docker backend" + str(run_args))
        return run_cmd(run_args, exec_opts)
