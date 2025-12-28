"""
The responsibility of this file and the similar ones under each command, is to translate the logic of the bmde interface
into the specification of the pure logic of the command, for example, translating shell into a corresponding entrypoint
"""

from __future__ import annotations

from pathlib import Path
from subprocess import Popen
from typing import Optional

from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import RunService
from .settings import RunSettings
from .spec import RunSpec, RunSpecOpts
from ...core.file_utils import resolve_nds
from ...core.opts import RunSpecExecOpts
from ...core.types import DockerOutputOptions, RunBackendOptions

log = logging.get_logger(__name__)


def create_run_spec(
    nds_rom: Optional[Path],
    directory: Optional[Path],
    arguments: Optional[list[str]] = None,
    arm9_debug_port: Optional[int] = 1000,
    backend: Optional[RunBackendOptions] = None,
    background: Optional[bool] = False,
    debug: Optional[bool] = False,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    docker_network: Optional[str] = None,
    fat_image: Optional[Path] = None,
    graphical_output: Optional[DockerOutputOptions] = None,
    settings: Optional[RunSettings] = None,
) -> RunSpec:
    """
    Creates the RunSpec from the provided arguments.
    Useful for the API to generate a spec without executing it immediately.
    """

    if directory is None:
        directory = Path.cwd()

    nds_resolved, _ = resolve_nds(nds_rom, cwd=directory)

    if settings is None:
        settings = RunSettings()

    # Default args are prepended to CLI args, not overridden
    passed_args: list[str] = []
    if arguments is not None:
        passed_args += arguments
    if settings.execution_settings.arguments is not None:
        passed_args += settings.execution_settings.arguments

    return RunSpec(
        RunSpecOpts=RunSpecOpts(
            nds_rom=nds_resolved,
            arguments=passed_args,
            arm9_debug_port=(
                arm9_debug_port
                if arm9_debug_port is not None
                else settings.arm9_debug_port
            ),
            debug=(
                debug
                if debug is not None
                else (settings.debug if settings.debug is not None else False)
            ),
            entrypoint=(
                entrypoint
                if entrypoint is not None
                else settings.execution_settings.entrypoint
            ),
            docker_network=(
                docker_network
                if docker_network is not None
                else settings.docker_network
            ),
            fat_image=fat_image if fat_image is not None else settings.fat_image,
            graphical_output=(
                graphical_output
                if graphical_output is not None
                else settings.graphical_output
            ),
        ),
        RunSpecExecOpts=RunSpecExecOpts(
            backend=backend if backend is not None else settings.backend,
            background=(
                background
                if background is not None
                else (
                    settings.execution_settings.background
                    if settings.execution_settings.background is not None
                    else False
                )
            ),
            dry_run=(
                dry_run if dry_run is not None else settings.execution_settings.dry_run
            ),
        ),
    )


def execute_run(
    spec: RunSpec,
) -> int | Popen[bytes]:
    """
    Executes the RunSpec.
    The API can call this directly with a pre-constructed spec.
    """

    handle = RunService().run(
        spec.RunSpecOpts,
        ExecOptions(
            dry_run=spec.RunSpecExecOpts.dry_run,
            background=spec.RunSpecExecOpts.background,
        ),
    )

    return handle


def run_command(
    nds_rom: Optional[Path],
    directory: Optional[Path],
    arguments: Optional[list[str]] = None,
    arm9_debug_port: Optional[int] = 1000,
    backend: Optional[RunBackendOptions] = None,
    background: Optional[bool] = False,
    debug: bool = False,
    docker_network: Optional[str] = None,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    fat_image: Optional[Path] = None,
    graphical_output: Optional[DockerOutputOptions] = None,
    settings: Optional[RunSettings] = None,
) -> int | Popen[bytes]:
    """
    CLI Entrypoint. Orchestrates spec creation and execution.
    """

    spec = create_run_spec(
        nds_rom=nds_rom,
        directory=directory,
        arguments=arguments,
        arm9_debug_port=arm9_debug_port,
        backend=backend,
        background=background,
        debug=debug,
        docker_network=docker_network,
        dry_run=dry_run,
        entrypoint=entrypoint,
        fat_image=fat_image,
        graphical_output=graphical_output,
        settings=settings,
    )

    return execute_run(spec)
