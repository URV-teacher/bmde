"""
Defines the schema of settings of the application
"""

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from bmde.commands.build.settings import BuildSettings
from bmde.commands.debug.settings import DebugSettings
from bmde.commands.git.settings import GitSettings
from bmde.commands.patch.settings import PatchSettings
from bmde.commands.run.settings import RunSettings
from bmde.config.logging_settings import LoggingSettings


class Settings(BaseSettings):
    """Configuration of BMDE."""

    # Environment variables are BMDE_<SECTION>__<KEY>, with __ between every level (e.g.
    # BMDE_RUN__EXECUTION_SETTINGS__BACKEND=docker), because the keys themselves contain single underscores
    model_config = SettingsConfigDict(env_prefix="BMDE_", env_nested_delimiter="__", extra="ignore")

    logging: LoggingSettings = LoggingSettings()
    run: RunSettings = RunSettings()
    build: BuildSettings = BuildSettings()
    git: GitSettings = GitSettings()
    patch: PatchSettings = PatchSettings()
    debug: DebugSettings = DebugSettings()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Settings() are the defaults. bmde.config.loader reads the files and the environment itself, so it can tell
        # which source supplied each value (bmde config --show-sources)
        return (init_settings,)
