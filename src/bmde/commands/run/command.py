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
from .service import RunService
from .spec import RunSpec
from ...core.file_utils import resolve_nds

log = logging.get_logger(__name__)


def run_command(
    nds: Optional[Path],
    image: Optional[Path],
    arguments: Optional[tuple[str]],
    background: Optional[bool],
    settings: Settings,
    dry_run: bool = False,
    docker_network: Optional[str] = None,
) -> int | Popen[bytes]:
    nds, assumed = resolve_nds(nds, cwd=Path.cwd())
    spec = RunSpec(
        nds=nds,
        image=(Path(image) if image else None),
        environment=settings.run.backend,
        docker_screen=settings.run.docker_screen,
        entrypoint=settings.run.entrypoint,
        debug=settings.run.debug,
        port=settings.run.port,
        arguments=arguments,
        dry_run=dry_run,
        docker_network=docker_network,
    )
    return RunService().run(spec, ExecOptions(dry_run=dry_run, background=background))
