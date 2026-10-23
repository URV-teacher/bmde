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
from typing import Annotated

import typer

from bmde.commands.config.command import config_command, show_sources_command
from bmde.config.schema import Settings


def config_controller(
    ctx: typer.Context,
    section: Annotated[
        str | None,
        typer.Argument(help="Command (e.g. run, git) or section (e.g. git.vpn) to configure. If omitted, all of them."),
    ] = None,
    file: Annotated[
        Path | None,
        typer.Option(
            "-f",
            "--file",
            dir_okay=False,
            help="bmde.toml file to write. If omitted, asks whether to use the repository or the user config.",
        ),
    ] = None,
    advanced: Annotated[
        bool,
        typer.Option("-a", "--advanced", help="Also ask for the advanced options (entrypoint, arguments...)"),
    ] = False,
    show_sources: Annotated[
        bool,
        typer.Option(
            "--show-sources",
            help="Instead of configuring, list the configuration files and variables that were read and which of them "
            "supplied each value",
        ),
    ] = False,
) -> None:
    """Interactively configure bmde or one of its commands, showing the current values as defaults."""
    settings: Settings = ctx.obj["settings"]
    if show_sources:
        show_sources_command(
            settings=settings, sources=ctx.obj["sources"], cli_overrides=ctx.obj["cli_overrides"], section=section
        )
        return
    config_command(settings=settings, section=section, file=file, advanced=advanced)
