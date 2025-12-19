import shutil

from .backend import PatchBackend
from ..spec import PatchSpec
from ...core.exec import run_cmd, ExecOptions


class HostRunner(PatchBackend):
    def is_available(self) -> bool:
        return shutil.which("dlditool")

    def run(self, spec: PatchSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("dlditool"))
        if not entry:
            return 127
        args = [entry, str(spec.d)]
        #if spec.image:
        #    args += ["--cflash-image", str(spec.image)]
        #if spec.debug:
        #    args += ["--arm9gdb-port", str(spec.port), "--gdb-stub"]
        args += list(spec.arguments)
        return run_cmd(args, exec_opts)
