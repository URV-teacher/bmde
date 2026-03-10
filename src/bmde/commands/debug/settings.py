from pydantic import BaseModel

from bmde.commands.run.settings import RunSettings
from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DockerOutputOptions


class DebugSettings(BaseModel):
    run: RunSettings = RunSettings()
    execution_settings: ExecutionSettings = ExecutionSettings()

    docker_screen: DockerOutputOptions | None = DockerOutputOptions.HOST
    docker_network: str | None = None
