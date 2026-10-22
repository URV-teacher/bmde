# bmde - Bare Metal Development Environment CLI
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from pathlib import Path
from subprocess import Popen

from bmde.core import logging
from bmde.core.exec import ExecOptions

from ...config.loader import load_settings
from ...core.docker import configure_docker_from_settings
from ...core.file_utils import resolve_nds
from ...core.logging import configure_logging_from_settings
from ...core.spec_opts import SpecExecOpts
from ...core.types import BackendOptions
from .service import PatchService
from .settings import PatchSettings
from .spec import PatchSpec, PatchSpecOpts

log = logging.get_logger(__name__)


def create_patch_spec(
    d: Path | None,
    nds_rom: Path | None = None,
    arguments: list[str] | None = None,
    backend: BackendOptions | None = None,
    background: bool = False,
    dry_run: bool = False,
    entrypoint: Path | None = None,
    interactive: bool = True,
    settings: PatchSettings | None = None,
) -> PatchSpec:

    if d is None:
        d = Path.cwd()

    nds_resolved, _ = resolve_nds(nds_rom, cwd=d)

    if settings is None:
        settings = PatchSettings()

    return PatchSpec(
        PatchSpecOpts=PatchSpecOpts(nds_rom=nds_resolved),
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
            entrypoint=(entrypoint if entrypoint is not None else settings.execution_settings.entrypoint),
            arguments=arguments,
            dry_run=(dry_run if dry_run is not None else settings.execution_settings.dry_run),
            background=(background if background is not None else settings.execution_settings.background),
            interactive=interactive,
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
            interactive=spec.SpecExecOpts.interactive,
        ),
    )


def patch_command(
    d: Path | None,
    nds_rom: Path | None = None,
    arguments: list[str] | None = None,
    backend: BackendOptions | None = None,
    background: bool = False,
    dry_run: bool = False,
    entrypoint: Path | None = None,
    interactive: bool = True,
    settings: PatchSettings | None = None,
) -> int | Popen[bytes]:

    if settings is None:
        full_settings = load_settings()
        configure_logging_from_settings(settings=full_settings)
        configure_docker_from_settings(settings=full_settings)
        settings = full_settings.patch

    spec = create_patch_spec(
        d=d,
        nds_rom=nds_rom,
        arguments=arguments,
        backend=backend,
        background=background,
        dry_run=dry_run,
        entrypoint=entrypoint,
        interactive=interactive,
        settings=settings,
    )

    return execute_patch(spec)
