from __future__ import annotations

import os
from pathlib import Path
from subprocess import Popen
from typing import Optional

from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import BuildService
from .settings import BuildSettings
from .spec import BuildSpec, BuildSpecOpts
from ...config.loader import load_settings
from ...core.logging import configure_logging_from_settings
from ...core.spec_opts import SpecExecOpts
from ...core.types import BackendOptions

log = logging.get_logger(__name__)


def create_build_spec(
    d: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    background: bool = False,
    interactive: bool = True,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    settings: Optional[BuildSettings] = None,
) -> BuildSpec:
    """
    Creates the BuildSpec from the provided arguments.
    """
    if d is None:
        d = Path(os.getcwd())

    if settings is None:
        settings = BuildSettings()

    # Default args are prepended to CLI args
    passed_args: list[str] = []
    if arguments is not None:
        passed_args += arguments
    if settings.execution_settings.arguments is not None:
        passed_args += settings.execution_settings.arguments

    return BuildSpec(
        BuildSpecOpts=BuildSpecOpts(
            d=d,
        ),
        SpecExecOpts=SpecExecOpts(
            backend=backend if backend is not None else (settings.execution_settings.backend if settings.execution_settings.backend is not None else BackendOptions.DOCKER),
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
            interactive=(
                interactive
                if interactive is not None
                else settings.execution_settings.interactive
            ),
        ),
    )


def execute_build(spec: BuildSpec) -> int | Popen[bytes]:
    """
    Executes the BuildSpec.
    """
    return BuildService().run(
        spec.BuildSpecOpts,
        ExecOptions(
            dry_run=spec.SpecExecOpts.dry_run,
            background=spec.SpecExecOpts.background,
            interactive=spec.SpecExecOpts.interactive,
        ),
    )


def build_command(
    d: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    background: bool = False,
    interactive: bool = True,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    settings: Optional[BuildSettings] = None,
) -> int | Popen[bytes]:
    """
    CLI Entrypoint. Orchestrates spec creation and execution.
    """
    if settings is None:
        full_settings = load_settings()
        configure_logging_from_settings(
            settings=full_settings
        )
        settings = full_settings.build

    spec = create_build_spec(
        d=d,
        arguments=arguments,
        backend=backend,
        background=background,
        interactive=interactive,
        dry_run=dry_run,
        entrypoint=entrypoint,
        settings=settings,
    )

    return execute_build(spec)
