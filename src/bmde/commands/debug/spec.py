from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.commands.run.spec import RunSpec
from bmde.core.types import DockerOutputOptions, BackendOptions


@dataclass
class DebugSpec(BaseSpec):
    RunSpec: RunSpec
    elf: Path
    environment: Optional[BackendOptions]
    docker_screen: Optional[DockerOutputOptions]
    entrypoint: Optional[Path]
    arguments: Optional[list[str]]
    dry_run: bool
