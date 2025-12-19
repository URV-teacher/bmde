import logging
import shutil
from pathlib import Path
from .base import BuildBackend
from ..spec import BuildSpec
from ...core.exec import run_cmd, ExecOptions

log = logging.getLogger(__name__)


class HostRunner(BuildBackend):
    def is_available(self) -> bool:
        return shutil.which("make")

    def run(self, spec: BuildSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("make"))
        if not entry:
            return 127
        args = [entry, str(spec.d)]
        #if spec.image:
        #    args += ["--cflash-image", str(spec.image)]
        #if spec.debug:
        #    args += ["--arm9gdb-port", str(spec.port), "--gdb-stub"]
        args += list(spec.arguments)
        return run_cmd(args, exec_opts)
