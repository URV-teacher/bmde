"""
The responsibility of this file and the similar ones under each command, is to translate the logic of the bmde interface
into the specification of the pure logic of the command, for example, translating shell into a corresponding entrypoint
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions, run_cmd
from .service import DebugService
from .spec import DebugSpec
from ..run.service import RunService
from ..run.spec import RunSpec
from ...core.file_utils import resolve_elf, resolve_nds

log = logging.get_logger(__name__)


def debug_command(
    nds: Optional[Path],
    elf: Optional[Path],
    image: Optional[Path],
    arguments: Optional[tuple[str]],
    settings: Settings,
    dry_run: bool = False,
) -> None:
    nds, assumed = resolve_nds(nds, cwd=Path.cwd())
    elf, assumed = resolve_elf(elf, cwd=Path.cwd())
    spec = DebugSpec(
        RunSpec=RunSpec(
            nds=nds,
            image=(Path(image) if image else None),
            environment=settings.debug.run.backend,
            docker_screen=settings.debug.run.docker_screen,
            entrypoint=settings.debug.run.entrypoint,
            debug=settings.debug.run.debug,
            port=settings.debug.run.port,
            arguments=arguments,
            dry_run=dry_run,
        ),
        elf=elf,
        environment=settings.debug.backend,
        docker_screen=settings.debug.docker_screen,
        entrypoint=settings.debug.entrypoint,
        arguments=arguments,
        dry_run=dry_run,
    )
    run_cmd(["docker", "network", "create", "bmde-debug"], ExecOptions())
    RunService().run(spec.RunSpec, ExecOptions(dry_run=dry_run, background=True))
    code = DebugService().run(spec, ExecOptions(dry_run=dry_run))
    run_cmd(["docker", "network", "rm", "bmde-debug"], ExecOptions())
    raise SystemExit(code)
