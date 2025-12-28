from __future__ import annotations

import os
from pathlib import Path
from subprocess import Popen
from typing import Optional

from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import PatchService
from .settings import PatchSettings
from .spec import PatchSpec, PatchSpecOpts
from ...core.spec_opts import SpecExecOpts
from ...core.types import BackendOptions

log = logging.get_logger(__name__)


def create_patch_spec(
    d: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    background: bool = False,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    settings: Optional[PatchSettings] = None,
) -> PatchSpec:
    if d is None:
        d = Path(os.getcwd())

    if settings is None:
        settings = PatchSettings()

    return PatchSpec(
        PatchSpecOpts=PatchSpecOpts(
            d=d,
        ),
        SpecExecOpts=SpecExecOpts(
            backend=(
                backend
                if backend is not None
                else (
                    settings.backend
                    if settings.backend is not None
                    else BackendOptions.DOCKER
                )
            ),
            entrypoint=(
                entrypoint
                if entrypoint is not None
                else settings.execution_settings.entrypoint
            ),
            arguments=arguments,
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


def execute_patch(spec: PatchSpec) -> int | Popen[bytes]:
    return PatchService().run(
        spec.PatchSpecOpts,
        ExecOptions(
            dry_run=spec.SpecExecOpts.dry_run,
            background=spec.SpecExecOpts.background,
            entrypoint=spec.SpecExecOpts.entrypoint,
            arguments=spec.SpecExecOpts.arguments,
            backend=spec.SpecExecOpts.backend,
        ),
    )


def patch_command(
    d: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    background: bool = False,
    dry_run: bool = False,
    entrypoint: Optional[Path] = None,
    settings: Optional[PatchSettings] = None,
) -> int | Popen[bytes]:
    spec = create_patch_spec(
        d=d,
        arguments=arguments,
        backend=backend,
        background=background,
        dry_run=dry_run,
        entrypoint=entrypoint,
        settings=settings,
    )

    return execute_patch(spec)
