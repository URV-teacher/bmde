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
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Docker screen: {str(docker_screen)}\n"
        f"- NDS ROM: {str(nds)}\n"
    )

    # CLI overrides
    if backend is not None:
        settings.run.execution_settings.backend = backend
    if entrypoint is not None:
        settings.run.execution_settings.entrypoint = entrypoint
    if port:
        settings.run.arm9_debug_port = port
    if docker_screen:
        settings.run.graphical_output = docker_screen

    log.debug(
        "Settings override:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Backend: {str(settings.run.execution_settings.backend)}\n"
        f"- Entrypoint: {str(settings.run.execution_settings.entrypoint)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- Docker screen: {str(settings.run.graphical_output)}\n"
        f"- NDS ROM: {str(nds)}\n"
    )
    debug_command(
        nds=nds,
        elf=elf,
        arguments=arguments,
        settings=settings,
        dry_run=dry_run,
    )
