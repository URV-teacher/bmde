import typer

from bmde.commands.debug.command import debug_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    ArgumentsOpt,
    BackendOpt,
    BackgroundOpt,
    DebuggerOpt,
    DockerScreenOpt,
    DryRunOpt,
    ElfRomOpt,
    EntrypointOpt,
    NdsRomOpt,
    PortOpt,
)

log = logging.get_logger(__name__)


def debug_controller(
    ctx: typer.Context,
    nds: NdsRomOpt = None,
    elf: ElfRomOpt = None,
    arguments: ArgumentsOpt = None,
    debugger: DebuggerOpt = None,
    docker_screen: DockerScreenOpt = None,
    # common flags
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    entrypoint: EntrypointOpt = None,
    port: PortOpt = None,
    dry_run: DryRunOpt = False,
) -> None:
    """Debugs an NDS ROM: runs it in desmume in debug mode, and a debugger (Insight by default) connected to it."""

    settings: Settings = ctx.obj["settings"]

    log.debug(
        "CLI options provided:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Backend: {str(backend)}\n"
        f"- Background: {str(background)}\n"
        f"- Debugger: {str(debugger)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Docker screen: {str(docker_screen)}\n"
        f"- NDS ROM: {str(nds)}\n"
        f"- ELF: {str(elf)}\n"
        f"- Port: {str(port)}\n"
    )

    ret = debug_command(
        nds=nds,
        elf=elf,
        arguments=arguments,
        backend=backend,
        background=background,
        debugger=debugger,
        docker_screen=docker_screen,
        dry_run=dry_run,
        entrypoint=entrypoint,
        port=port,
        settings=settings.debug,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
