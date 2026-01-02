import os
import subprocess

from bmde.core import logging
from bmde.core.docker import can_run_docker
from bmde.core.exec import run_cmd, ExecOptions
from .backend import PatchBackend
from ..spec import PatchSpecOpts

log = logging.get_logger(__name__)


class DockerRunner(PatchBackend):
    def is_available(self) -> bool:
        return can_run_docker()

    def run(
        self, spec: PatchSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        entry = []
        if exec_opts.entrypoint:
            entry = ["--entrypoint", str(exec_opts.entrypoint)]

        docker_img = "aleixmt/dlditool:latest"

        mounts = [
            "-v",
            f"{spec.nds_rom.parent}:/input/{os.path.basename(spec.nds_rom.parent)}:rw",
        ]
        workdir_opt = [
            "-w",
            f"/input/{os.path.basename(spec.nds_rom.parent)}",
        ]  # Workdir

        arguments = []
        if exec_opts.arguments is not None:
            arguments = list(exec_opts.arguments)
        else:
            arguments = [
                "mpcf.dldi",
                f"/input/{os.path.basename(spec.nds_rom.parent)}/{os.path.basename(spec.nds_rom)}",
            ]

        run_args = [
            "docker",
            "run",
            "--pull=always",
            "--rm",
            "-it",
            *mounts,
            *entry,
            *workdir_opt,
            docker_img,
            *arguments,
        ]

        log.debug("Patch arguments for Docker backend" + str(run_args))
        return run_cmd(run_args, exec_opts)
