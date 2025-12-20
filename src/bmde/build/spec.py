from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from bmde.core.types import BackendName


@dataclass
class BuildSpec:
    d: Path
    environment: Optional[BackendName]
    entrypoint: Optional[str]
    arguments: Optional[Sequence[str]]
    dry_run: Optional[bool]


