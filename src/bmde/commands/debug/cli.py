import typer

from bmde.cli import app
from bmde.commands.debug.command import debug_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    NdsRomOpt,
    ArgumentsOpt,
    DockerScreenOpt,
    EntrypointOpt,
    PortOpt,
    DryRunOpt,
    ElfRomOpt,
    BackendOpt,
    BackgroundOpt,
)

log = logging.get_logger(__name__)


@app.command("debug")
def debug_controller(
    ctx: typer.Context,
    nds: NdsRomOpt = None,
    elf: ElfRomOpt = None,
    arguments: ArgumentsOpt = None,
    docker_screen: DockerScreenOpt = None,
    # common flags
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    entrypoint: EntrypointOpt = None,
    port: PortOpt = 1000,
    dry_run: DryRunOpt = False,
) -> None:
    """desmume wrapper. Runs an NDS ROM."""

    settings: Settings = ctx.obj["settings"]

    log.debug(
        "CLI options provided:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Backend: {str(backend)}\n"
        f"- Background: {str(background)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Docker screen: {str(docker_screen)}\n"
        f"- NDS ROM: {str(nds)}\n"
    )

    log.debug(
        "Final settings for debug command:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Backend: {str(backend if backend is not None else settings.debug.backend)}\n"
        f"- Background: {str(background)}\n"
        f"- Entrypoint: {str(entrypoint if entrypoint is not None else settings.debug.execution_settings.entrypoint)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- Docker screen: {str(docker_screen if docker_screen is not None else settings.debug.docker_screen)}\n"
        f"- NDS ROM: {str(nds)}\n"
    )

    ret = debug_command(
        nds=nds,
        elf=elf,
        arguments=arguments,
        backend=backend,
        background=background,
        docker_screen=docker_screen,
        dry_run=dry_run,
        entrypoint=entrypoint,
        port=port,
        settings=settings.debug,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
