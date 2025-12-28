import shutil
import subprocess

from bmde.core import logging
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available
from .backend import GitBackend
from ..spec import GitSpecOpts

log = logging.get_logger(__name__)


class HostRunner(GitBackend):
    def is_available(self) -> bool:
        return is_command_available("git")

    def run(
        self, spec: GitSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        entry = (
            str(exec_opts.entrypoint) if exec_opts.entrypoint else (shutil.which("git"))
        )
        if not entry:
            return 127
        args = [entry]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        log.debug("Arguments for git in host backend: " + str(args))
        return run_cmd(args, exec_opts)
