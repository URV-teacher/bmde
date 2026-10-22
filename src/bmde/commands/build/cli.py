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
