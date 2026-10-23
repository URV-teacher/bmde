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

from bmde.commands.run.command import run_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    ArgumentsOpt,
    BackendOpt,
    BackgroundOpt,
    ControlsOpt,
    DebugOpt,
    DirectoryOpt,
    DockerNetworkOpt,
    DockerScreenOpt,
    DryRunOpt,
    EntrypointOpt,
    FatImageOpt,
    InteractiveOpt,
    NdsRomOpt,
    PortOpt,
    SoundOpt,
)

log = logging.get_logger(__name__)


def run_controller(
    ctx: typer.Context,
    nds_rom: NdsRomOpt = None,
    directory: DirectoryOpt = None,
    arguments: ArgumentsOpt = None,
    arm9_debug_port: PortOpt = None,
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    interactive: InteractiveOpt = True,
    debug: DebugOpt = None,
    docker_network: DockerNetworkOpt = None,
    dry_run: DryRunOpt = False,
    entrypoint: EntrypointOpt = None,
    fat_image: FatImageOpt = None,
    graphical_output: DockerScreenOpt = None,
    sound: SoundOpt = None,
    controls: ControlsOpt = None,
) -> None:
    log.debug(
        "CLI options provided:\n"
        "- Arguments:\n"
        f"- NDS ROM: {nds_rom!s}\n"
        f"- Rom directory: {directory!s}\n"
        "- Behavioural parameters:\n"
        f"- Arguments: {arguments!s}\n"
        f"- ARM 9 debug port: {arm9_debug_port!s}\n"
        f"- Backend: {backend!s}\n"
        f"- Background: {background!s}\n"
        f"- Interactive: {interactive!s}\n"
        f"- Debug: {debug!s}\n"
        f"- Docker Network: {docker_network!s}\n"
        f"- Dry run: {dry_run!s}\n"
        f"- Entrypoint: {entrypoint!s}\n"
        f"- FAT image: {fat_image!s}\n"
        f"- Graphical output: {graphical_output!s}\n"
        f"- Sound: {sound!s}\n"
        f"- Controls: {controls!s}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.debug(f"Loaded settings:\n{settings.run!s}\n")
    ret = run_command(
        nds_rom=nds_rom,
        directory=directory,
        arguments=arguments,
        arm9_debug_port=arm9_debug_port,
        backend=backend,
        background=background,
        interactive=interactive,
        debug=debug,
        docker_network=docker_network,
        dry_run=dry_run,
        entrypoint=entrypoint,
        fat_image=fat_image,
        graphical_output=graphical_output,
        sound=sound,
        controls=controls,
        settings=settings.run,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
