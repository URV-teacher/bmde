from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions


@dataclass
class SpecExecOpts(BaseSpec):
    backend: BackendOptions
    background: bool
    dry_run: bool
    entrypoint: Optional[Path]
    arguments: Optional[list[str]]
