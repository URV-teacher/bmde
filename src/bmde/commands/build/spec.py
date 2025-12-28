from dataclasses import dataclass
from pathlib import Path

from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts


@dataclass
class BuildSpecOpts(BaseSpec):
    d: Path


@dataclass
class BuildSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    BuildSpecOpts: BuildSpecOpts


