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

from pydantic import BaseModel, Field

from bmde.commands.run.settings import RunSettings
from bmde.config.command_settings import ExecutionSettings
from bmde.core.types import DebuggerOptions, DockerOutputOptions


class DebugSettings(BaseModel):
    """Settings of the debug command."""

    # Settings of the emulator run in debug mode
    run: RunSettings = RunSettings()
    execution_settings: ExecutionSettings = ExecutionSettings()

    debugger: DebuggerOptions | None = Field(
        default=DebuggerOptions.INSIGHT, description="Debugger connected to the emulator"
    )
    docker_screen: DockerOutputOptions | None = Field(
        default=DockerOutputOptions.HOST, description='Method to show the debugger screen with the "docker" backend'
    )
