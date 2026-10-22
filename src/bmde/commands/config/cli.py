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
