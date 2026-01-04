import typer

from bmde.cli import app
from bmde.commands.run.command import run_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    NdsRomOpt,
    FatImageOpt,
    ArgumentsOpt,
    DockerScreenOpt,
    EntrypointOpt,
    DebugOpt,
    PortOpt,
    DryRunOpt,
    DirectoryOpt,
    DockerNetworkOpt,
    BackgroundOpt,
    InteractiveOpt,
    BackendOpt,
)

log = logging.get_logger(__name__)


@app.command("run")
def run_controller(
    ctx: typer.Context,
    nds_rom: NdsRomOpt = None,
    directory: DirectoryOpt = None,
    arguments: ArgumentsOpt = None,
    arm9_debug_port: PortOpt = 1024,
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    interactive: InteractiveOpt = True,
    debug: DebugOpt = False,
    docker_network: DockerNetworkOpt = None,
    dry_run: DryRunOpt = False,
    entrypoint: EntrypointOpt = None,
    fat_image: FatImageOpt = None,
    graphical_output: DockerScreenOpt = None,
) -> None:

    log.debug(
        "CLI options provided:\n"
        "- Arguments:\n"
        f"- NDS ROM: {str(nds_rom)}\n"
        f"- Rom directory: {str(directory)}\n"
        "- Behavioural parameters:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- ARM 9 debug port: {str(arm9_debug_port)}\n"
        f"- Backend: {str(backend)}\n"
        f"- Background: {str(background)}\n"
        f"- Interactive: {str(interactive)}\n"
        f"- Debug: {str(debug)}\n"
        f"- Docker Network: {str(docker_network)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- FAT image: {str(fat_image)}\n"
        f"- Graphical output: {str(graphical_output)}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.debug("Loaded settings:\n" f"{str(settings.run)}\n")
    run_command(
        nds_rom=nds_rom,
        directory=directory,
        arguments=arguments,
        arm9_debug_port=arm9_debug_port,
        backend=backend,
        background=background,
        interactive=interactive,
        debug=debug,
        docker_network=docker_network,
        dry_run=dry_run,
        entrypoint=entrypoint,
        fat_image=fat_image,
        graphical_output=graphical_output,
        settings=settings.run,
    )
