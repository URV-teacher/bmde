import typer

from bmde.commands.run.command import run_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import (
    ArgumentsOpt,
    BackendOpt,
    BackgroundOpt,
    ControlsOpt,
    DebugOpt,
    DirectoryOpt,
    DockerNetworkOpt,
    DockerScreenOpt,
    DryRunOpt,
    EntrypointOpt,
    FatImageOpt,
    InteractiveOpt,
    NdsRomOpt,
    PortOpt,
    SoundOpt,
)

log = logging.get_logger(__name__)


def run_controller(
    ctx: typer.Context,
    nds_rom: NdsRomOpt = None,
    directory: DirectoryOpt = None,
    arguments: ArgumentsOpt = None,
    arm9_debug_port: PortOpt = None,
    backend: BackendOpt = None,
    background: BackgroundOpt = False,
    interactive: InteractiveOpt = True,
    debug: DebugOpt = None,
    docker_network: DockerNetworkOpt = None,
    dry_run: DryRunOpt = False,
    entrypoint: EntrypointOpt = None,
    fat_image: FatImageOpt = None,
    graphical_output: DockerScreenOpt = None,
    sound: SoundOpt = None,
    controls: ControlsOpt = None,
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
        f"- Sound: {str(sound)}\n"
        f"- Controls: {str(controls)}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.debug(f"Loaded settings:\n{str(settings.run)}\n")
    ret = run_command(
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
        sound=sound,
        controls=controls,
        settings=settings.run,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
