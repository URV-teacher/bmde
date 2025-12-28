from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DockerOutputOptions
from bmde.core.types import DOCKER_DESMUME_DEBUG_NETWORK


class RunSettings(BaseModel):
    graphical_output: Optional[DockerOutputOptions] = DockerOutputOptions.HOST

    execution_settings: ExecutionSettings = ExecutionSettings()

    debug: Optional[bool] = False
    arm9_debug_port: Optional[int] = 1000
    fat_image: Optional[Path] = None
    docker_network: Optional[str] = DOCKER_DESMUME_DEBUG_NETWORK
