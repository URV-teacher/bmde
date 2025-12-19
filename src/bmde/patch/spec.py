from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from bmde.core.types import BackendName


@dataclass
class PatchSpec:
    d: Path
    environment: Optional[BackendName]
    entrypoint: Optional[str]
    arguments: Sequence[str]
    shell: bool
    dry_run: bool


