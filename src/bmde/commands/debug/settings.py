from typing import Optional

from pydantic import BaseModel

from bmde.commands.run.settings import RunSettings
from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import BackendOptions, DockerOutputOptions


class DebugSettings(BaseModel):
    run: RunSettings = RunSettings()
    execution_settings: ExecutionSettings = ExecutionSettings()

    backend: Optional[BackendOptions] = None
    docker_screen: Optional[DockerOutputOptions] = None
    docker_network: Optional[str] = None
