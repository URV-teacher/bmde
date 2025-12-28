from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel


class ExecutionSettings(BaseModel):
    entrypoint: Optional[Path] = None
    arguments: Optional[List[str]] = None
    background: Optional[bool] = None
    dry_run: Optional[bool] = None
