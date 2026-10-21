import shutil
import subprocess

from bmde.core import logging
from bmde.core.docker import docker_project_dir
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import is_command_available
from bmde.core.types import DebuggerOptions

from ..spec import DebugSpecOpts
from .backend import DebugBackend

log = logging.get_logger(__name__)

# Executables of each debugger, by order of preference
DEBUGGER_COMMANDS = {
    DebuggerOptions.INSIGHT: ["arm-eabi-insight", "insight"],
    DebuggerOptions.GDB_MULTIARCH: ["gdb-multiarch"],
}


class HostRunner(DebugBackend):
    def is_available(self) -> bool:
        return any(is_command_available(c) for commands in DEBUGGER_COMMANDS.values() for c in commands)

    def run(self, spec: DebugSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:
        if exec_opts.entrypoint is not None:
            entry = str(exec_opts.entrypoint)
        else:
            commands = DEBUGGER_COMMANDS[spec.debugger]
            entry = next(
                (path for c in commands if (path := shutil.which(c)) is not None),
                commands[0],
            )

        # The emulator publishes its GDB stub in the host, also when it runs in Docker
        port = spec.RunSpec.RunSpecOpts.arm9_debug_port
        target = f"localhost:{port if port is not None else 1024}"

        # ELFs built with Docker refer to the sources in the path where the project was mounted
        project = spec.elf.parent
        args = [
            entry,
            "-ex",
            f"set substitute-path {docker_project_dir(project)} {project}",
        ]
        if spec.debugger == DebuggerOptions.INSIGHT:
            log.info(f'Connect from Insight with "Run > Connect to target": Remote/TCP, {target}')
        else:
            args += ["-ex", f"target remote {target}"]
        args += [str(spec.elf)]

        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        return run_cmd(args, exec_opts)
