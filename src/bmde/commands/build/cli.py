import os
from pathlib import Path

import typer

from bmde.cli import app
from bmde.commands.build.command import build_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import ArgumentsOpt, DirectoryOpt, BackendOpt, EntrypointOpt, DryRunOpt, BackgroundOpt

log = logging.get_logger(__name__)


@app.command("build")
def build_controller(
        ctx: typer.Context,
        directory: DirectoryOpt = Path(os.getcwd()),
        arguments: ArgumentsOpt = None,
        backend: BackendOpt = None,
        background: BackgroundOpt = False,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False
) -> None:
    """devkitARM make wrapper. Builds NDS ROM from source code."""

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Background: {str(background)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              )

    settings: Settings = ctx.obj["settings"]

    log.debug("Loaded settings:\n" f"{str(settings.build)}\n")

    build_command(
        d=directory,
        arguments=arguments,
        backend=backend,
        background=background,
        entrypoint=entrypoint,
        dry_run=dry_run,
        settings=settings.build
    )
