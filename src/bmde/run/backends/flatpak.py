import shutil
from .base import RunnerBackend
from ..spec import RunSpec
from ...core.exec import run_cmd, ExecOptions


class FlatpakRunner(RunnerBackend):
    def is_available(self) -> bool:
        return shutil.which("flatpak")

    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int:
        # Adjust to your flatpak package and args
        args = ["flatpak", "run", "org.desmume.DesmuME", str(spec.nds)]
        return run_cmd(args, exec_opts)
