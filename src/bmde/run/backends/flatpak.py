import shutil
from .backend import RunBackend
from ..spec import RunSpec
from ...core.exec import run_cmd, ExecOptions


class FlatpakRunner(RunBackend):
    def is_available(self) -> bool:
        return shutil.which("flatpak")

    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int:
        # Adjust to your flatpak package and args
        args = ["flatpak", "run", "org.desmume.DesmuME", str(spec.nds)]
        return run_cmd(args, exec_opts)
