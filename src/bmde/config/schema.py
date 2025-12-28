"""
Defines the schema of settings of the application
"""

from pydantic import BaseModel

from bmde.config.logging_settings import LoggingSettings
from bmde.commands.build.settings import BuildSettings
from bmde.commands.run.settings import RunSettings
from bmde.commands.git.settings import GitSettings
from bmde.commands.patch.settings import PatchSettings
from bmde.commands.debug.settings import DebugSettings


class Settings(BaseModel):
    logging: LoggingSettings = LoggingSettings()
    run: RunSettings = RunSettings()
    build: BuildSettings = BuildSettings()
    git: GitSettings = GitSettings()
    patch: PatchSettings = PatchSettings()
    debug: DebugSettings = DebugSettings()
