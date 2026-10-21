"""
Defines the schema of settings of the application
"""

from pydantic import BaseModel

from bmde.commands.build.settings import BuildSettings
from bmde.commands.debug.settings import DebugSettings
from bmde.commands.git.settings import GitSettings
from bmde.commands.patch.settings import PatchSettings
from bmde.commands.run.settings import RunSettings
from bmde.config.docker_settings import DockerSettings
from bmde.config.logging_settings import LoggingSettings


class Settings(BaseModel):
    """Configuration of BMDE."""

    logging: LoggingSettings = LoggingSettings()
    docker: DockerSettings = DockerSettings()
    run: RunSettings = RunSettings()
    build: BuildSettings = BuildSettings()
    git: GitSettings = GitSettings()
    patch: PatchSettings = PatchSettings()
    debug: DebugSettings = DebugSettings()
