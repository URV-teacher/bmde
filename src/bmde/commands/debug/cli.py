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
        f"- Arguments: {arguments!s}\n"
        f"- Backend: {backend!s}\n"
        f"- Background: {background!s}\n"
        f"- Debugger: {debugger!s}\n"
        f"- Entrypoint: {entrypoint!s}\n"
        f"- Docker screen: {docker_screen!s}\n"
        f"- NDS ROM: {nds!s}\n"
        f"- ELF: {elf!s}\n"
        f"- Port: {port!s}\n"
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
