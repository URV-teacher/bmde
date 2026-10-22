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

from typing import Any

import typer

from bmde.commands.build.service import BuildService
from bmde.commands.debug.service import DebugService
from bmde.commands.git.service import GitService
from bmde.commands.patch.service import PatchService
from bmde.commands.run.service import RunService
from bmde.config.loader import load_settings
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.logging import configure_logging_from_settings
from bmde.core.service import Service
from bmde.core.types import BackendOptions

log = logging.get_logger(__name__)


def check_command(settings: Settings | None = None) -> None:

    if settings is None:
        settings = load_settings()
        configure_logging_from_settings(settings=settings)

    services: list[tuple[str, Service[Any, Any], BackendOptions | None]] = [
        ("Git", GitService(), settings.git.execution_settings.backend),
        ("Run", RunService(), settings.run.execution_settings.backend),
        ("Build", BuildService(), settings.build.execution_settings.backend),
        ("Debug", DebugService(), settings.debug.execution_settings.backend),
        ("Patch", PatchService(), settings.patch.execution_settings.backend),
    ]

    msg = (
        "\nSummary of backend availability for the BMDE services in this machine (🚫 means not available, ✅ means "
        "available):\n"
    )
    for name, service, selected_backend in services:
        msg += f"\n  * Service: {name}\n"

        if selected_backend:
            backend_impl = service.mapping.get(selected_backend)
            if backend_impl:
                available = backend_impl.is_available()
                icon = "✅" if available else "🚫"
                msg += f"    Selected backend: {selected_backend.value} {icon}\n"
            else:
                msg += f"    Selected backend: {selected_backend.value} (Unknown backend?)\n"
        else:
            msg += "    Selected backend: Auto (None configured)\n"

        msg += "    Other backends for this service (by order of preference):\n"
        for backend_opt in service.order:
            if selected_backend and backend_opt == selected_backend:
                continue

            # Every backend of the order has an implementation (as Service.choose_backend expects)
            icon = "✅" if service.mapping[backend_opt].is_available() else "🚫"
            msg += f"      - {backend_opt.value}: {icon}\n"

    typer.echo(msg)
