from dataclasses import dataclass
from pathlib import Path

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions


@dataclass
class SpecExecOpts(BaseSpec):
    backend: BackendOptions
    background: bool
    dry_run: bool
    interactive: bool
    entrypoint: Path | None
    arguments: list[str] | None
