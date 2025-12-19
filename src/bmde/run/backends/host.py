import logging
import shutil
from pathlib import Path
from .backend import RunBackend
from ..spec import RunSpec
from ...core.exec import run_cmd, ExecOptions

log = logging.getLogger(__name__)


class HostRunner(RunBackend):
    def is_available(self) -> bool:
        return shutil.which("desmume") or shutil.which("desmume-cli")

    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("desmume") or shutil.which("desmume-cli"))
        if not entry:
            return 127
        args = [entry, str(spec.nds)]
        if spec.image:
            args += ["--cflash-image", str(spec.image)]
        if spec.debug:
            args += ["--arm9gdb-port", str(spec.port), "--gdb-stub"]
        args += list(spec.arguments)
        return run_cmd(args, exec_opts)
