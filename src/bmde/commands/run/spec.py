from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec_opts import RunSpecExecOpts
from bmde.core.spec import BaseSpec
from bmde.core.types import DockerOutputOptions


@dataclass
class RunSpecOpts(BaseSpec):
    nds_rom: Path
    arm9_debug_port: Optional[int]
    debug: bool
    docker_network: Optional[str]
    fat_image: Optional[Path]
    graphical_output: Optional[DockerOutputOptions]


@dataclass
class RunSpec(BaseSpec):
    RunSpecExecOpts: RunSpecExecOpts
    RunSpecOpts: RunSpecOpts
