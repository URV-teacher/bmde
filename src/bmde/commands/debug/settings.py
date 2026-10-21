from pydantic import BaseModel, Field

from bmde.commands.run.settings import RunSettings
from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DebuggerOptions, DockerOutputOptions


class DebugSettings(BaseModel):
    """Settings of the debug command."""

    # Settings of the emulator run in debug mode
    run: RunSettings = RunSettings()
    execution_settings: ExecutionSettings = ExecutionSettings()

    debugger: DebuggerOptions | None = Field(
        default=DebuggerOptions.INSIGHT, description="Debugger connected to the emulator"
    )
    docker_screen: DockerOutputOptions | None = Field(
        default=DockerOutputOptions.HOST, description='Method to show the debugger screen with the "docker" backend'
    )
