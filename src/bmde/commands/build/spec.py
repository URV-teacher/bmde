from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions


@dataclass
class BuildSpec(BaseSpec):
    d: Path
    backend: Optional[BackendOptions]
    entrypoint: Optional[Path]
    arguments: Optional[list[str]]
    dry_run: Optional[bool]


