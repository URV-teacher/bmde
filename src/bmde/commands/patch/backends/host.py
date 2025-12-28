import shutil
import subprocess

from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available
from .backend import PatchBackend
from ..spec import PatchSpecOpts


class HostRunner(PatchBackend):
    def is_available(self) -> bool:
        return is_command_available("dlditool")

    def run(
        self, spec: PatchSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            dlditool_path = shutil.which("dlditool")
            if dlditool_path is None:
                entry = "dlditool"
            else:
                entry = dlditool_path
        args = [entry, str(spec.d)]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
