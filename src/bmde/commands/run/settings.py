from pathlib import Path

from pydantic import BaseModel, Field

from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DOCKER_DESMUME_DEBUG_NETWORK, DockerOutputOptions


class RunSettings(BaseModel):
    """Settings of the emulator."""

    graphical_output: DockerOutputOptions | None = Field(
        default=DockerOutputOptions.HOST,
        description='Method to show the emulator screen with the "docker" backend: a desktop window (host), VNC on '
        "port 5900 of localhost (vnc) or not shown (none)",
    )

    execution_settings: ExecutionSettings = ExecutionSettings()

    debug: bool | None = Field(default=False, description="Enable the GDB stub of the emulator if supported")
    arm9_debug_port: int | None = Field(default=1024, description="Port of the GDB stub of the ARM9 processor")
    fat_image: Path | None = Field(default=None, description="Path to a FAT image loaded into the emulator")
    sound: bool | None = Field(default=True, description="Play the emulator sound on the host")
    controls: Path | None = Field(
        default=None, description="Path to a DeSmuME desmume.ini with custom controls (and HUD options)"
    )
    docker_network: str | None = Field(
        default=DOCKER_DESMUME_DEBUG_NETWORK,
        description='Name of the Docker network shared by the emulator and the debugger with the "docker" backend',
        json_schema_extra={"advanced": True},
    )
