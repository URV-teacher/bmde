import os
import shutil
import subprocess

from bmde.core import logging
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import is_command_available

from ..spec import BuildSpecOpts
from .backend import BuildBackend

log = logging.get_logger(__name__)


class HostRunner(BuildBackend):
    def is_available(self) -> bool:
        return self.check()

    def check(self) -> bool:
        checks_passed = True

        # Check make
        if not is_command_available("make"):
            log.error("'make' not found in PATH.")
            checks_passed = False
        else:
            log.debug("'make' found.")

        # Check devkitARM tools
        if not is_command_available("arm-none-eabi-gcc"):
            log.error("'arm-none-eabi-gcc' (devkitARM) not found in PATH.")
            checks_passed = False
        else:
            log.debug("'arm-none-eabi-gcc' found.")

        # Check DEVKITPRO env vartk

        if "DEVKITPRO" not in os.environ:
            log.warning(
                "DEVKITPRO environment variable not set. Some tools might fail."
            )

        # Check DEVKITARM env var
        if "DEVKITARM" not in os.environ:
            log.warning("DEVKITARM environment variable not set.")

        return checks_passed

    def run(
        self, spec: BuildSpecOpts, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            make_path = shutil.which("make")
            entry = "make" if make_path is None else make_path
        args = [entry, str(spec.d)]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
