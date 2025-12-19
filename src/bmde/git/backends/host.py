import logging
import shutil

from .backend import GitBackend
from ..spec import GitSpec
from ...core.exec import run_cmd, ExecOptions

log = logging.getLogger(__name__)

class HostRunner(GitBackend):
    def is_available(self) -> bool:
        return shutil.which("git")

    def run(self, spec: GitSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("git"))
        if not entry:
            return 127
        args = []
        args += list(spec.arguments)
        log.debug("Arguments for git in host backend: " + str(args))
        return run_cmd(args, exec_opts)
