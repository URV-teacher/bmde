from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import RunBackendOptions, DockerOutputOptions


@dataclass
class RunSpec(BaseSpec):
    nds: Path
    image: Optional[Path]
    environment: Optional[RunBackendOptions]
    docker_screen: Optional[DockerOutputOptions]
    entrypoint: Optional[Path]
    debug: bool
    port: int
    arguments: Optional[tuple[str]]
    dry_run: bool
