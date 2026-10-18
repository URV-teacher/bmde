from pydantic import BaseModel

from bmde.commands.run.settings import RunSettings
from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DebuggerOptions, DockerOutputOptions


class DebugSettings(BaseModel):
    # Settings of the emulator run in debug mode
    run: RunSettings = RunSettings()
    execution_settings: ExecutionSettings = ExecutionSettings()

    debugger: DebuggerOptions | None = DebuggerOptions.INSIGHT
    docker_screen: DockerOutputOptions | None = DockerOutputOptions.HOST
