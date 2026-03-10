from dataclasses import dataclass
from pathlib import Path

from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts
from bmde.core.types import DockerOutputOptions


@dataclass
class RunSpecOpts(BaseSpec):
    nds_rom: Path
    arm9_debug_port: int | None
    debug: bool
    docker_network: str
    fat_image: Path | None
    graphical_output: DockerOutputOptions | None


@dataclass
class RunSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    RunSpecOpts: RunSpecOpts
