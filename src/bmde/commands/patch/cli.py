import typer

from bmde.cli import app
from bmde.commands.patch.command import patch_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    ArgumentsOpt,
    DirectoryOpt,
    BackendOpt,
    EntrypointOpt,
    DryRunOpt,
    BackgroundOpt,
)

log = logging.get_logger(__name__)


@app.command("patch")
def patch_controller(
    ctx: typer.Context,
    arguments: ArgumentsOpt = None,
    directory: DirectoryOpt = None,
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    entrypoint: EntrypointOpt = None,
    dry_run: DryRunOpt = False,
) -> None:
    """dlditool wrapper. Patches a NDS ROM for FAT usage."""

    log.debug(
        "CLI options provided:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Directory: {str(directory)}\n"
        f"- Backend: {str(backend)}\n"
        f"- Background: {str(background)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Dry run: {str(dry_run)}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.debug(
        "Final settings for build command:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Directory: {str(directory)}\n"
        f"- Backend: {str(backend if backend is not None else settings.patch.execution_settings.backend)}\n"
        f"- Background: {str(background)}\n"
        f"- Entrypoint: {str(entrypoint if entrypoint is not None else settings.patch.execution_settings.entrypoint)}\n"
    )

    ret = patch_command(
        d=directory,
        arguments=arguments,
        backend=backend,
        background=background,
        entrypoint=entrypoint,
        dry_run=dry_run,
        settings=settings.patch,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
