from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions


@dataclass
class PatchSpec(BaseSpec):
    d: Path
    environment: Optional[BackendOptions]
    entrypoint: Optional[Path]
    arguments: Optional[tuple[str]]
    dry_run: bool
