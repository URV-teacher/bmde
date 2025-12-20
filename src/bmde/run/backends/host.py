import shutil

from .backend import RunBackend
from ..spec import RunSpec
from ...core import logging
from ...core.exec import run_cmd, ExecOptions
from ...core.os_utils import is_command_available

log = logging.get_logger(__name__)


class HostRunner(RunBackend):
    def is_available(self) -> bool:
        return is_command_available("desmume") or is_command_available("desmume-cli")


    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or shutil.which("desmume") or shutil.which("desmume-cli")
        args = [entry, str(spec.nds)]
        if spec.image:
            args += ["--cflash-image", str(spec.image)]
        if spec.debug:
            args += ["--arm9gdb-port", str(spec.port), "--gdb-stub"]
        args += list(spec.arguments)
        return run_cmd(args, exec_opts)
