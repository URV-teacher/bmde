import typer

from bmde.cli import app
from bmde.commands.run.command import run_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.shared_options import NdsRomOpt, FatImageOpt, ArgumentsOpt, DockerScreenOpt, RunBackendOpt, \
    EntrypointOpt, DebugOpt, PortOpt, DryRunOpt

log = logging.get_logger(__name__)


@app.command("run")
def run_controller(
    ctx: typer.Context,
    nds: NdsRomOpt = None,
    image: FatImageOpt = None,
    arguments: ArgumentsOpt = None,
    docker_screen: DockerScreenOpt = None,
    # common flags
    backend: RunBackendOpt = None,
    entrypoint: EntrypointOpt = None,
    debug: DebugOpt = False,
    port: PortOpt = 1000,
    dry_run: DryRunOpt = False,
) -> None:
    """desmume wrapper. Runs an NDS ROM."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Docker screen: {str(docker_screen)}\n"
              f"- NDS ROM: {str(nds)}\n"
              )

    # CLI overrides
    if backend is not None:
        settings.run.backend = backend
    if entrypoint is not None:
        settings.run.entrypoint = entrypoint
    if debug:
        settings.run.debug = True
    if port:
        settings.run.port = port
    if docker_screen:
        settings.run.docker_screen = docker_screen

    log.debug("Settings override:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Backend: {str(settings.run.backend)}\n"
              f"- Entrypoint: {str(settings.run.entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Docker screen: {str(settings.run.docker_screen)}\n"
              f"- NDS ROM: {str(nds)}\n"
              )
    run_command(
        nds=nds,
        image=image,
        arguments=arguments,
        settings=settings,
        dry_run=dry_run
    )
