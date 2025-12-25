"""
The responsibility of this file and the similar ones under each command, is to translate the logic of the bmde interface
into the specification of the pure logic of the command, for example, translating shell into a corresponding entrypoint
"""

from __future__ import annotations

from pathlib import Path
from subprocess import Popen
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import DebugService
from .spec import DebugSpec
from ..run.command import run_command
from ..run.spec import RunSpec
from ...core.docker import ensure_network_is_present, docker_remove_network
from ...core.file_utils import resolve_elf, resolve_nds
from ...core.types import DOCKER_DESMUME_DEBUG_NETWORK

log = logging.get_logger(__name__)


def debug_command(
    nds: Optional[Path],
    elf: Optional[Path],
    arguments: Optional[list[str]],
    settings: Settings,
    dry_run: bool = False,
) -> None:
    nds, assumed = resolve_nds(nds, cwd=Path.cwd())
    print("nds" + str(nds))
    print("assumed" + str(assumed))
    elf, assumed = resolve_elf(elf, cwd=Path.cwd())
    spec = DebugSpec(
        RunSpec=RunSpec(
            nds=nds,
            image=settings.debug.run.image,
            environment=settings.debug.run.backend,
            docker_screen=settings.debug.run.docker_screen,
            entrypoint=settings.debug.run.entrypoint,
            debug=True,
            port=settings.debug.run.port,
            arguments=arguments,
            dry_run=dry_run,
            docker_network=DOCKER_DESMUME_DEBUG_NETWORK,
        ),
        elf=elf,
        environment=settings.debug.backend,
        docker_screen=settings.debug.docker_screen,
        entrypoint=settings.debug.entrypoint,
        arguments=arguments,
        dry_run=dry_run,
    )
    ensure_network_is_present(DOCKER_DESMUME_DEBUG_NETWORK)
    handle = run_command(
        nds=nds,
        image=settings.debug.run.image,
        arguments=settings.debug.run.arguments,
        settings=settings,
        background=True,
    )
    code = DebugService().run(spec, ExecOptions(dry_run=dry_run))
    if isinstance(handle, Popen):
        handle.communicate()

    docker_remove_network(DOCKER_DESMUME_DEBUG_NETWORK)
    raise SystemExit(code)
