from dataclasses import dataclass
from pathlib import Path

from bmde.commands.run.spec import RunSpec
from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts
from bmde.core.types import DockerOutputOptions


@dataclass
class DebugSpecOpts(BaseSpec):
    elf: Path
    docker_screen: DockerOutputOptions | None
    docker_network: str | None
    RunSpec: RunSpec


@dataclass
class DebugSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    DebugSpecOpts: DebugSpecOpts
