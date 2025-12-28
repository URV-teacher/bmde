from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel

from bmde.core.types import BackendOptions


class ExecutionSettings(BaseModel):
    entrypoint: Optional[Path] = None
    arguments: Optional[List[str]] = None
    background: Optional[bool] = False
    dry_run: Optional[bool] = False
    backend: Optional[BackendOptions] = BackendOptions.DOCKER
