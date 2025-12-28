
from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings


class BuildSettings(BaseModel):
    execution_settings: ExecutionSettings = ExecutionSettings()
