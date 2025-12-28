from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings


class PatchSettings(BaseModel):

    execution_settings: ExecutionSettings = ExecutionSettings()
