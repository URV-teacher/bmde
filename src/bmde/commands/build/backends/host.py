import shutil
import subprocess

from bmde.core import logging
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available
from .backend import BuildBackend
from ..spec import BuildSpecOpts

log = logging.get_logger(__name__)


class HostRunner(BuildBackend):
    def is_available(self) -> bool:
        return is_command_available("make")


    def run(self, spec: BuildSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            make_path = shutil.which("make")
            if make_path is None:
                entry = "make"
            else:
                entry = make_path
        args = [entry, str(spec.d)]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
