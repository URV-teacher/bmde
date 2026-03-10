import shutil
import subprocess

from bmde.core.exec import ExecOptions, run_cmd

from ..spec import RunSpecOpts
from .backend import RunBackend


class FlatpakRunner(RunBackend):
    def is_available(self) -> bool:
        return shutil.which("flatpak") is not None

    def run(
        self, spec: RunSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        # Adjust to your flatpak package and args
        args = ["flatpak", "run", "org.desmume.DesmuME", str(spec.nds_rom)]
        return run_cmd(args, exec_opts)
