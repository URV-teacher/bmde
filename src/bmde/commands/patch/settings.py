from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings


class PatchSettings(BaseModel):
    """Settings of the patch command."""

    execution_settings: ExecutionSettings = ExecutionSettings()
