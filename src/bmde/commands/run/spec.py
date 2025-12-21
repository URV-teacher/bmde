from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Literal

from bmde.core.types import RunBackendName

RunDockerOutputName = Literal["vnc", "host"]

@dataclass
class RunSpec:
    nds: Path
    image: Optional[Path]
    environment: Optional[RunBackendName]
    docker_screen: Optional[RunDockerOutputName]
    entrypoint: Optional[str]
    debug: bool
    port: int
    arguments: Sequence[str]
    dry_run: bool


