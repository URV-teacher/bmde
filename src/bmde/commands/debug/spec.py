from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.commands.run.spec import RunSpec
from bmde.core.spec_opts import SpecExecOpts
from bmde.core.types import DockerOutputOptions


@dataclass
class DebugSpecOpts(BaseSpec):
    elf: Path
    docker_screen: Optional[DockerOutputOptions]
    docker_network: Optional[str]
    RunSpec: RunSpec


@dataclass
class DebugSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    DebugSpecOpts: DebugSpecOpts
