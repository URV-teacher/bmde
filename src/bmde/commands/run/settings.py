from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import RunBackendOptions, DockerOutputOptions


class RunSettings(BaseModel):
    backend: Optional[RunBackendOptions] = None
    graphical_output: Optional[DockerOutputOptions] = None

    execution_settings: ExecutionSettings = ExecutionSettings()

    debug: Optional[bool] = None
    arm9_debug_port: Optional[int] = None
    fat_image: Optional[Path] = None
    docker_network: Optional[str] = None
