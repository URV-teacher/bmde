from dataclasses import dataclass
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions, RunBackendOptions


@dataclass
class RunSpecExecOpts(BaseSpec):
    backend: Optional[RunBackendOptions]
    background: bool
    dry_run: bool


@dataclass
class SpecExecOpts(BaseSpec):
    backend: Optional[BackendOptions]
    background: bool
    dry_run: bool
