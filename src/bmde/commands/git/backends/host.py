import shutil

from .backend import GitBackend
from ..spec import GitSpec
from bmde.core import logging
from bmde.core.exec import run_cmd, ExecOptions
from bmde.core.os_utils import is_command_available

log = logging.get_logger(__name__)

class HostRunner(GitBackend):
    def is_available(self) -> bool:
        return is_command_available("git")

    def run(self, spec: GitSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("git"))
        if not entry:
            return 127
        args = [entry]
        args += list(spec.arguments)
        log.debug("Arguments for git in host backend: " + str(args))
        return run_cmd(args, exec_opts)
