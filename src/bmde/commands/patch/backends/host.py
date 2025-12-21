import shutil

from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available
from .backend import PatchBackend
from ..spec import PatchSpec


class HostRunner(PatchBackend):
    def is_available(self) -> bool:
        return is_command_available("dlditool")

    def run(self, spec: PatchSpec, exec_opts: ExecOptions) -> int:
        if spec.entrypoint is not None:
            entry = str(spec.entrypoint)
        else:
            dlditool_path = shutil.which("dlditool")
            if dlditool_path is None:
                entry = "dlditool"
            else:
                entry = dlditool_path
        args = [entry, str(spec.d)]
        if spec.arguments is not None:
            args += list(spec.arguments)
        return run_cmd(args, exec_opts)
