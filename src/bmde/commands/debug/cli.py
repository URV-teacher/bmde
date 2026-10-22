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

from bmde.commands.debug.command import debug_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    ArgumentsOpt,
    BackendOpt,
    BackgroundOpt,
    DebuggerOpt,
    DockerScreenOpt,
    DryRunOpt,
    ElfRomOpt,
    EntrypointOpt,
    NdsRomOpt,
    PortOpt,
)

log = logging.get_logger(__name__)


def debug_controller(
    ctx: typer.Context,
    nds: NdsRomOpt = None,
    elf: ElfRomOpt = None,
    arguments: ArgumentsOpt = None,
    debugger: DebuggerOpt = None,
    docker_screen: DockerScreenOpt = None,
    # common flags
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    entrypoint: EntrypointOpt = None,
    port: PortOpt = None,
    dry_run: DryRunOpt = False,
) -> None:
    """Debugs an NDS ROM: runs it in desmume in debug mode, and a debugger (Insight by default) connected to it."""
    settings: Settings = ctx.obj["settings"]

    log.debug(
        "CLI options provided:\n"
        f"- Arguments: {arguments!s}\n"
        f"- Backend: {backend!s}\n"
        f"- Background: {background!s}\n"
        f"- Debugger: {debugger!s}\n"
        f"- Entrypoint: {entrypoint!s}\n"
        f"- Docker screen: {docker_screen!s}\n"
        f"- NDS ROM: {nds!s}\n"
        f"- ELF: {elf!s}\n"
        f"- Port: {port!s}\n"
    )

    ret = debug_command(
        nds=nds,
        elf=elf,
        arguments=arguments,
        backend=backend,
        background=background,
        debugger=debugger,
        docker_screen=docker_screen,
        dry_run=dry_run,
        entrypoint=entrypoint,
        port=port,
        settings=settings.debug,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
