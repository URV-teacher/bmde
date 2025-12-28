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
from ...core.spec_opts import SpecExecOpts
from ...core.types import (
    DockerOutputOptions,
    BackendOptions,
    DOCKER_DESMUME_DEBUG_NETWORK,
)

log = logging.get_logger(__name__)


def create_run_spec(
    nds_rom: Optional[Path],
    directory: Optional[Path],
    arguments: Optional[list[str]] = None,
    arm9_debug_port: Optional[int] = None,
    backend: Optional[BackendOptions] = None,
    background: Optional[bool] = None,
    debug: Optional[bool] = None,
    dry_run: Optional[bool] = None,
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
            docker_network=(
                docker_network
                if docker_network is not None
                else (
                    settings.docker_network
                    if settings.docker_network is not None
                    else DOCKER_DESMUME_DEBUG_NETWORK
                )
            ),
            fat_image=fat_image if fat_image is not None else settings.fat_image,
            graphical_output=(
                graphical_output
                if graphical_output is not None
                else settings.graphical_output
            ),
        ),
        SpecExecOpts=SpecExecOpts(
            backend=(
                backend
                if backend is not None
                else (
                    settings.execution_settings.backend
                    if settings.execution_settings.backend is not None
                    else BackendOptions.DOCKER
                )
            ),
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
                dry_run
                if dry_run is not None
                else (
                    settings.execution_settings.dry_run
                    if settings.execution_settings.dry_run is not None
                    else False
                )
            ),
            entrypoint=(
                entrypoint
                if entrypoint is not None
                else settings.execution_settings.entrypoint
            ),
            arguments=passed_args,
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
            dry_run=spec.SpecExecOpts.dry_run,
            background=spec.SpecExecOpts.background,
            entrypoint=spec.SpecExecOpts.entrypoint,
            arguments=spec.SpecExecOpts.arguments,
            backend=spec.SpecExecOpts.backend,
        ),
    )

    return handle


def run_command(
    nds_rom: Optional[Path],
    directory: Optional[Path],
    arguments: Optional[list[str]] = None,
    arm9_debug_port: Optional[int] = 1000,
    backend: Optional[BackendOptions] = None,
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
