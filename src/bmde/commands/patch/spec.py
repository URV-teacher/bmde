from dataclasses import dataclass
from pathlib import Path

from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts


@dataclass
class PatchSpecOpts(BaseSpec):
    nds_rom: Path


@dataclass
class PatchSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    PatchSpecOpts: PatchSpecOpts
