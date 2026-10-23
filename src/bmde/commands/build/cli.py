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

import typer

from bmde.commands.build.command import build_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    ArgumentsOpt,
    BackendOpt,
    BackgroundOpt,
    DirectoryOpt,
    DryRunOpt,
    EntrypointOpt,
    InteractiveOpt,
)

log = logging.get_logger(__name__)


def build_controller(
    ctx: typer.Context,
    directory: DirectoryOpt = None,
    arguments: ArgumentsOpt = None,
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    interactive: InteractiveOpt = True,
    entrypoint: EntrypointOpt = None,
    dry_run: DryRunOpt = False,
) -> None:
    """DevkitARM make wrapper. Builds NDS ROM from source code."""
    settings: Settings = ctx.obj["settings"]

    log.debug(
        "CLI options provided:\n"
        f"- Arguments: {arguments!s}\n"
        f"- Directory: {directory!s}\n"
        f"- Backend: {backend!s}\n"
        f"- Background: {background!s}\n"
        f"- Interactive: {interactive!s}\n"
        f"- Entrypoint: {entrypoint!s}\n"
        f"- Dry run: {dry_run!s}\n"
    )

    ret = build_command(
        d=directory,
        arguments=arguments,
        backend=backend,
        background=background,
        interactive=interactive,
        entrypoint=entrypoint,
        dry_run=dry_run,
        settings=settings.build,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
