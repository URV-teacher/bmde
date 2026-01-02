import typer
from typing import Any, List, Tuple, Optional

from bmde.config.loader import load_settings
from bmde.core import logging
from bmde.core.logging import configure_logging_from_settings
from bmde.core.service import Service
from bmde.core.types import BackendOptions
from bmde.config.schema import Settings
from bmde.commands.git.service import GitService
from bmde.commands.run.service import RunService
from bmde.commands.build.service import BuildService
from bmde.commands.debug.service import DebugService
from bmde.commands.patch.service import PatchService

log = logging.get_logger(__name__)


def check_command(settings: Settings) -> None:

    if settings is None:
        full_settings = load_settings()
        configure_logging_from_settings(
            settings=full_settings,
            obfuscate_sensibles=full_settings.logging.hide_sensibles,
        )

    services: List[Tuple[str, Service[Any, Any], Optional[BackendOptions]]] = [
        ("Git", GitService(), settings.git.execution_settings.backend),
        ("Run", RunService(), settings.run.execution_settings.backend),
        ("Build", BuildService(), settings.build.execution_settings.backend),
        ("Debug", DebugService(), settings.debug.execution_settings.backend),
        ("Patch", PatchService(), settings.patch.execution_settings.backend),
    ]

    msg = "\nSummary of backend availability for the BMDE services in this machine (🚫 means not available, ✅ means available):\n"
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

            backend_impl = service.mapping.get(backend_opt)
            if backend_impl:
                available = backend_impl.is_available()
                icon = "✅" if available else "🚫"
                msg += f"      - {backend_opt.value}: {icon}\n"

    typer.echo(msg)
