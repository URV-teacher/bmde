from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec_opts import SpecExecOpts
from bmde.core.spec import BaseSpec
from bmde.core.types import DockerOutputOptions


@dataclass
class RunSpecOpts(BaseSpec):
    nds_rom: Path
    arm9_debug_port: Optional[int]
    debug: bool
    docker_network: str
    fat_image: Optional[Path]
    graphical_output: Optional[DockerOutputOptions]


@dataclass
class RunSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    RunSpecOpts: RunSpecOpts
