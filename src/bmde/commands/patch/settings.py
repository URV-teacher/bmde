from typing import Optional

from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import BackendOptions


class PatchSettings(BaseModel):
    backend: Optional[BackendOptions] = None

    execution_settings: ExecutionSettings = ExecutionSettings()
