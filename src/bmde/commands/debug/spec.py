from dataclasses import dataclass
from pathlib import Path

from bmde.commands.run.spec import RunSpec
from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts
from bmde.core.types import DebuggerOptions, DockerOutputOptions


@dataclass
class DebugSpecOpts(BaseSpec):
    elf: Path
    debugger: DebuggerOptions
    docker_screen: DockerOutputOptions | None
    # Emulator to debug, run in debug mode
    RunSpec: RunSpec


@dataclass
class DebugSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    DebugSpecOpts: DebugSpecOpts
