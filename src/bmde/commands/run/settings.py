from pathlib import Path

from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DOCKER_DESMUME_DEBUG_NETWORK, DockerOutputOptions


class RunSettings(BaseModel):
    graphical_output: DockerOutputOptions | None = DockerOutputOptions.HOST

    execution_settings: ExecutionSettings = ExecutionSettings()

    debug: bool | None = False
    arm9_debug_port: int | None = 1024
    fat_image: Path | None = None
    docker_network: str | None = DOCKER_DESMUME_DEBUG_NETWORK
