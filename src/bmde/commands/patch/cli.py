import typer

from bmde.commands.patch.command import patch_command
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
    """Dlditool wrapper. Patches a NDS ROM for FAT usage."""
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
