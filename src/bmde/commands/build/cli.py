import os

import typer

from bmde.cli import app
from bmde.commands.build.command import build_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import ArgumentsOpt, DirectoryOpt, BackendOpt, EntrypointOpt, DryRunOpt

log = logging.get_logger(__name__)


@app.command("build")
def build_controller(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False
):
    """devkitARM make wrapper. Builds NDS ROM from source code."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              )

    # CLI overrides
    if backend is not None:
        settings.build.backend = backend
    if entrypoint is not None:
        settings.build.entrypoint = entrypoint

    log.debug("Final settings for build command:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Backend: {str(settings.build.backend)}\n"
              f"- Entrypoint: {str(settings.build.entrypoint)}\n"
              )

    build_command(
        d=directory,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )
