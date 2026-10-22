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

from bmde.core.types import BackendOptions


class ExecutionSettings(BaseModel):
    """How the command is executed."""

    entrypoint: Path | None = Field(
        default=None,
        description="Executable used instead of the default entrypoint of the backend",
        json_schema_extra={"advanced": True},
    )
    arguments: list[str] | None = Field(
        default=None, description="Arguments passed to the entrypoint", json_schema_extra={"advanced": True}
    )
    background: bool | None = Field(
        default=False, description="Run the command in the background", json_schema_extra={"advanced": True}
    )
    dry_run: bool | None = Field(
        default=False, description="Simulate actions without executing them", json_schema_extra={"advanced": True}
    )
    interactive: bool = Field(
        default=True, description="Run in interactive mode (allocates a TTY)", json_schema_extra={"advanced": True}
    )
    backend: BackendOptions | None = Field(
        default=None,
        description="Backend used to execute the command. If unset, the first available backend is used",
    )
