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

from pathlib import Path

from pydantic import BaseModel, Field

from bmde.core.types import LogLevel, get_default_log_path


class LoggingSettings(BaseModel):
    """Logging of the CLI."""

    level: LogLevel = Field(default=LogLevel.get_default_log_level(), description="Verbosity of the CLI output")
    file: Path | None = Field(
        default=get_default_log_path(),
        description="Path of the log file. If unset, a new timestamped file is created on each execution in the user "
        "log dir (~/.local/state/bmde/log on Linux, ~/Library/Logs/bmde on macOS, %LOCALAPPDATA%\\bmde\\Logs on "
        "Windows)",
        json_schema_extra={"dynamic_default": "<user log dir>/<date>.log"},
    )
    hide_sensibles: bool | None = Field(default=True, description="Hide sensitive values (e.g. passwords) in the logs")
