import shutil

from .backend import PatchBackend
from ..spec import PatchSpec
from ...core.exec import run_cmd, ExecOptions
from ...core.os_utils import is_command_available


class HostRunner(PatchBackend):
    def is_available(self) -> bool:
        return is_command_available("dlditool")

    def run(self, spec: PatchSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("dlditool"))
        if not entry:
            return 127
        args = [entry, str(spec.d)]
        args += list(spec.arguments)
        return run_cmd(args, exec_opts)
