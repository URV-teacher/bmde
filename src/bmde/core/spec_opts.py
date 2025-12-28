from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions, RunBackendOptions


@dataclass
class SpecExecOpts(BaseSpec):
    backend: Optional[BackendOptions]
    background: bool
    dry_run: bool
    entrypoint: Optional[Path]
    arguments: Optional[list[str]]


@dataclass
class RunSpecExecOpts(BaseSpec):
    backend: Optional[RunBackendOptions]
    background: bool
    dry_run: bool
    entrypoint: Optional[Path]
    arguments: Optional[list[str]]
