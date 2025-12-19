from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Literal

from bmde.core.types import Backend, BackendName


@dataclass
class BuildSpec:
    d: Path
    environment: Optional[BackendName]
    entrypoint: Optional[str]
    arguments: Sequence[str]
    dry_run: bool


