# bmde - Bare Metal Development Environment CLI
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Defines the schema of settings of the application."""

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from bmde.commands.build.settings import BuildSettings
from bmde.commands.debug.settings import DebugSettings
from bmde.commands.git.settings import GitSettings
from bmde.commands.patch.settings import PatchSettings
from bmde.commands.run.settings import RunSettings
from bmde.config.docker_settings import DockerSettings
from bmde.config.logging_settings import LoggingSettings


class Settings(BaseSettings):
    """Configuration of BMDE."""

    # Environment variables are BMDE_<SECTION>__<KEY>, with __ between every level (e.g.
    # BMDE_RUN__EXECUTION_SETTINGS__BACKEND=docker), because the keys themselves contain single underscores
    model_config = SettingsConfigDict(env_prefix="BMDE_", env_nested_delimiter="__", extra="ignore")

    logging: LoggingSettings = LoggingSettings()
    docker: DockerSettings = DockerSettings()
    run: RunSettings = RunSettings()
    build: BuildSettings = BuildSettings()
    git: GitSettings = GitSettings()
    patch: PatchSettings = PatchSettings()
    debug: DebugSettings = DebugSettings()

    @classmethod
    # The signature is the one pydantic-settings calls, so the sources that are not used keep their parameters
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],  # noqa: ARG003
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Settings() are the defaults. bmde.config.loader reads the files and the environment itself, so it can tell
        # which source supplied each value (bmde config --show-sources)
        return (init_settings,)
