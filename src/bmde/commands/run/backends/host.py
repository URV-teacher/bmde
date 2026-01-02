import shutil
import subprocess

from bmde.core import logging
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available
from .backend import RunBackend
from ..spec import RunSpecOpts

log = logging.get_logger(__name__)


class HostRunner(RunBackend):
    def is_available(self) -> bool:
        return self.check()

    def check(self) -> bool:
        available = is_command_available("desmume") or is_command_available(
            "desmume-cli"
        )
        if not available:
            log.error("desmume or desmume-cli not found in PATH.")
        return available

    def run(
        self, spec: RunSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            desmume_path = shutil.which("desmume")
            desmumecli_path = shutil.which("desmume-cli")
            if desmume_path is not None:
                entry = desmume_path
            elif desmumecli_path is not None:
                entry = desmumecli_path
            else:
                entry = "desmume"
        args = [entry, str(spec.nds_rom)]
        if spec.fat_image:
            args += ["--cflash-image", str(spec.fat_image)]
        if spec.debug:
            args += ["--arm9gdb-port", str(spec.arm9_debug_port), "--gdb-stub"]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
