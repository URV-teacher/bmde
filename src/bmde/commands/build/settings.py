from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings


class BuildSettings(BaseModel):
    """Settings of the build command."""

    execution_settings: ExecutionSettings = ExecutionSettings()
