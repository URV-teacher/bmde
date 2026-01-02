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
    InteractiveOpt,
)

log = logging.get_logger(__name__)


@app.command("patch")
def patch_controller(
    ctx: typer.Context,
    arguments: ArgumentsOpt = None,
    directory: DirectoryOpt = None,
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    interactive: InteractiveOpt = True,
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
        f"- Interactive: {str(interactive)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Dry run: {str(dry_run)}\n"
    )

    settings: Settings = ctx.obj["settings"]

    ret = patch_command(
        d=directory,
        arguments=arguments,
        backend=backend,
        background=background,
        interactive=interactive,
        entrypoint=entrypoint,
        dry_run=dry_run,
        settings=settings.patch,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
