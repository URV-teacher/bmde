import shutil
import subprocess

from bmde.core import logging
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available
from .backend import DebugBackend
from ..spec import DebugSpecOpts

log = logging.get_logger(__name__)


class HostRunner(DebugBackend):
    def is_available(self) -> bool:
        return is_command_available("insight")

    def run(
        self, spec: DebugSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            insight_path = shutil.which("desmume")
            if insight_path is not None:
                entry = insight_path
            else:
                entry = "insight"
        args = [entry, str(spec.elf)]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
