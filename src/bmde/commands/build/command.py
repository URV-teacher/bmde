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

import os
from pathlib import Path
from subprocess import Popen

from bmde.core import logging
from bmde.core.exec import ExecOptions

from ...config.loader import load_settings
from ...core.docker import configure_docker_from_settings
from ...core.logging import configure_logging_from_settings
from ...core.spec_opts import SpecExecOpts
from ...core.types import BackendOptions
from .service import BuildService
from .settings import BuildSettings
from .spec import BuildSpec, BuildSpecOpts

log = logging.get_logger(__name__)


def create_build_spec(
    d: Path | None,
    arguments: list[str] | None = None,
    backend: BackendOptions | None = None,
    background: bool = False,
    interactive: bool = True,
    dry_run: bool = False,
    entrypoint: Path | None = None,
    settings: BuildSettings | None = None,
) -> BuildSpec:
    """Creates the BuildSpec from the provided arguments."""
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
            backend=backend
            if backend is not None
            else (
                settings.execution_settings.backend
                if settings.execution_settings.backend is not None
                else BackendOptions.DOCKER
            ),
            entrypoint=(entrypoint if entrypoint is not None else settings.execution_settings.entrypoint),
            arguments=passed_args,
            dry_run=(dry_run if dry_run is not None else settings.execution_settings.dry_run),
            background=(background if background is not None else settings.execution_settings.background),
            interactive=(interactive if interactive is not None else settings.execution_settings.interactive),
        ),
    )


def execute_build(spec: BuildSpec) -> int | Popen[bytes]:
    """Executes the BuildSpec."""
    return BuildService().run(
        spec.BuildSpecOpts,
        ExecOptions(
            arguments=spec.SpecExecOpts.arguments,
            dry_run=spec.SpecExecOpts.dry_run,
            background=spec.SpecExecOpts.background,
            interactive=spec.SpecExecOpts.interactive,
            backend=spec.SpecExecOpts.backend,
            entrypoint=spec.SpecExecOpts.entrypoint,
        ),
    )


def build_command(
    d: Path | None,
    arguments: list[str] | None = None,
    backend: BackendOptions | None = None,
    background: bool = False,
    interactive: bool = True,
    dry_run: bool = False,
    entrypoint: Path | None = None,
    settings: BuildSettings | None = None,
) -> int | Popen[bytes]:
    """CLI Entrypoint. Orchestrates spec creation and execution."""
    if settings is None:
        full_settings = load_settings()
        configure_logging_from_settings(settings=full_settings)
        configure_docker_from_settings(settings=full_settings)
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
