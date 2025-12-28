import shutil
import subprocess

from bmde.core.exec import run_cmd, ExecOptions
from .backend import RunBackend
from ..spec import RunSpecOpts


class FlatpakRunner(RunBackend):
    def is_available(self) -> bool:
        if shutil.which("flatpak") is not None:
            return True
        return False

    def run(
        self, spec: RunSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        # Adjust to your flatpak package and args
        args = ["flatpak", "run", "org.desmume.DesmuME", str(spec.nds_rom)]
        return run_cmd(args, exec_opts)
