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
from .service import DebugService
from .settings import DebugSettings
from .spec import DebugSpec, DebugSpecOpts
from ..run.service import RunService
from ..run.spec import RunSpec, RunSpecOpts
from ...core.file_utils import resolve_elf, resolve_nds
from ...core.spec_opts import SpecExecOpts
from ...core.types import (
    DOCKER_DESMUME_DEBUG_NETWORK,
    BackendOptions,
    DockerOutputOptions,
)

log = logging.get_logger(__name__)


def create_debug_spec(
    nds: Optional[Path],
    elf: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    background: bool = False,
    docker_screen: Optional[DockerOutputOptions] = None,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    port: int = 1000,
    settings: Optional[DebugSettings] = None,
) -> DebugSpec:
    if settings is None:
        settings = DebugSettings()

    elf_resolved, _ = resolve_elf(elf, cwd=Path.cwd())
    nds_resolved, _ = resolve_nds(nds, cwd=Path.cwd())

    # Default args are prepended to CLI args
    passed_args: list[str] = []
    if arguments is not None:
        passed_args += arguments
    if settings.execution_settings.arguments is not None:
        passed_args += settings.execution_settings.arguments

    return DebugSpec(
        DebugSpecOpts=DebugSpecOpts(
            elf=elf_resolved,
            docker_screen=(
                docker_screen if docker_screen is not None else settings.docker_screen
            ),
            docker_network=settings.docker_network,
            RunSpec=RunSpec(
                RunSpecOpts=RunSpecOpts(
                    nds_rom=nds_resolved,
                    fat_image=settings.run.fat_image,
                    graphical_output=settings.run.graphical_output,
                    debug=True,
                    arm9_debug_port=(
                        settings.run.arm9_debug_port
                        if settings.run.arm9_debug_port is not None
                        else port
                    ),
                    docker_network=DOCKER_DESMUME_DEBUG_NETWORK,
                ),
                SpecExecOpts=SpecExecOpts(
                    dry_run=dry_run,
                    backend=(
                        settings.run.execution_settings.backend
                        if settings.run.execution_settings.backend is not None
                        else BackendOptions.DOCKER
                    ),
                    background=True,
                    entrypoint=settings.run.execution_settings.entrypoint,
                    arguments=arguments,
                ),
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
            entrypoint=(
                entrypoint
                if entrypoint is not None
                else settings.execution_settings.entrypoint
            ),
            arguments=passed_args,
            dry_run=(
                dry_run if dry_run is not None else settings.execution_settings.dry_run
            ),
            background=(
                background
                if background is not None
                else settings.execution_settings.background
            ),
        ),
    )


def execute_debug(spec: DebugSpec) -> int | Popen[bytes]:
    handle = RunService().run(
        spec.DebugSpecOpts.RunSpec.RunSpecOpts,
        ExecOptions(
            dry_run=spec.DebugSpecOpts.RunSpec.SpecExecOpts.dry_run,
            background=spec.DebugSpecOpts.RunSpec.SpecExecOpts.background,
            backend=spec.DebugSpecOpts.RunSpec.SpecExecOpts.backend,
            entrypoint=spec.DebugSpecOpts.RunSpec.SpecExecOpts.entrypoint,
            arguments=spec.DebugSpecOpts.RunSpec.SpecExecOpts.arguments,
        ),
    )

    code = DebugService().run(
        spec.DebugSpecOpts,
        ExecOptions(
            dry_run=spec.SpecExecOpts.dry_run,
            background=spec.SpecExecOpts.background,
            entrypoint=spec.SpecExecOpts.entrypoint,
            arguments=spec.SpecExecOpts.arguments,
            backend=spec.SpecExecOpts.backend,
        ),
    )

    if isinstance(handle, Popen):
        handle.communicate()

    return code


def debug_command(
    nds: Optional[Path],
    elf: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    background: bool = False,
    docker_screen: Optional[DockerOutputOptions] = None,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    port: int = 1000,
    settings: Optional[DebugSettings] = None,
) -> int | Popen[bytes]:
    spec = create_debug_spec(
        nds=nds,
        elf=elf,
        arguments=arguments,
        backend=backend,
        background=background,
        docker_screen=docker_screen,
        dry_run=dry_run,
        entrypoint=entrypoint,
        port=port,
        settings=settings,
    )

    return execute_debug(spec)
