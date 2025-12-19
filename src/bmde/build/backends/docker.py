import logging
import os
import subprocess

from .backend import BuildBackend
from ..spec import BuildSpec
from ...core.exec import run_cmd, ExecOptions
from ...core.os_utils import host_uid_gid

log = logging.getLogger(__name__)


class DockerRunner(BuildBackend):
    def is_available(self) -> bool:
        return True  # optionally check docker info

    def run(self, spec: BuildSpec, exec_opts: ExecOptions) -> int:
        entry = []
        if spec.entrypoint:
            entry = ["--entrypoint", str(spec.entrypoint) or "make"]

        if spec.shell:
            entry = ["--entrypoint", "bash"]
        docker_img = "aleixmt/bmde-linux:latest"

        dirname = os.path.basename(spec.d)
        mounts = ["-v", f"{spec.d}:/input/{dirname}:rw"]
        envs = []
        ports = []
        workdir_opt = ["-w", f"/input/{dirname}"]  # Workdir
        uid, gid = host_uid_gid()
        user_opt = ["--user", f"{uid}:{gid}"]

        run_args = ["docker", "run", "--pull=always", "--rm", "-it", *user_opt, *mounts, *envs, *ports, *entry,
                    *workdir_opt, docker_img,
                    *spec.arguments]

        return run_cmd(run_args, exec_opts)
