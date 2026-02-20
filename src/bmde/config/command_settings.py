from pathlib import Path

from pydantic import BaseModel

from bmde.core.types import BackendOptions


class ExecutionSettings(BaseModel):
    entrypoint: Path | None = None
    arguments: list[str] | None = None
    background: bool | None = False
    dry_run: bool | None = False
    interactive: bool = True
    backend: BackendOptions | None = None
