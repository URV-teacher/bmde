import shutil

from .backend import BuildBackend
from ..spec import BuildSpec
from ...core import logging
from ...core.exec import run_cmd, ExecOptions
from ...core.os_utils import is_command_available

log = logging.get_logger(__name__)


class HostRunner(BuildBackend):
    def is_available(self) -> bool:
        return is_command_available("make")


    def run(self, spec: BuildSpec, exec_opts: ExecOptions) -> int:
        entry = spec.entrypoint or (shutil.which("make"))
        args = [entry, str(spec.d)]
        args += list(spec.arguments)
        return run_cmd(args, exec_opts)
