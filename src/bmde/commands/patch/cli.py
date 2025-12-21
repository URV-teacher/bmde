import os

import typer

from bmde.cli import app
from bmde.commands.patch.command import patch_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import ArgumentsOpt, DirectoryOpt, BackendOpt, EntrypointOpt, DryRunOpt

log = logging.get_logger(__name__)


@app.command("patch")
def patch_controller(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False,
):
    """dlditool wrapper. Patches a NDS ROM for FAT usage."""

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
        settings.patch.backend = backend
    if entrypoint is not None:
        settings.patch.entrypoint = entrypoint

    log.debug("Final settings for build command:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(settings.patch.backend)}\n"
              f"- Entrypoint: {str(settings.patch.entrypoint)}\n"
              )

    patch_command(
        d=directory,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )