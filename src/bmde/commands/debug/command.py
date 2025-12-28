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
from ..run.service import RunService
from ..run.spec import RunSpec, RunSpecOpts
from ...core.file_utils import resolve_elf, resolve_nds
from ...core.spec_opts import RunSpecExecOpts
from ...core.types import DOCKER_DESMUME_DEBUG_NETWORK

log = logging.get_logger(__name__)


def debug_command(
    nds: Optional[Path],
    elf: Optional[Path],
    arguments: Optional[list[str]],
    settings: Settings,
    dry_run: bool = False,
) -> None:
    elf, assumed = resolve_elf(elf, cwd=Path.cwd())
    nds, assumed = resolve_nds(nds, cwd=Path.cwd())
    spec = DebugSpec(
        RunSpec=RunSpec(
            RunSpecOpts=RunSpecOpts(
                nds_rom=nds,
                fat_image=settings.debug.run.fat_image,
                graphical_output=settings.debug.run.graphical_output,
                debug=True,
                arm9_debug_port=settings.debug.run.arm9_debug_port,
                docker_network=DOCKER_DESMUME_DEBUG_NETWORK,
            ),
            RunSpecExecOpts=RunSpecExecOpts(
                dry_run=dry_run,
                backend=settings.debug.run.backend,
                background=True,
                entrypoint=settings.debug.run.execution_settings.entrypoint,
                arguments=arguments,
            ),
        ),
        elf=elf,
        backend=settings.debug.backend,
        docker_screen=settings.debug.docker_screen,
        entrypoint=settings.debug.execution_settings.entrypoint,
        arguments=arguments,
        dry_run=dry_run,
    )

    handle = RunService().run(spec.RunSpec.RunSpecOpts, ExecOptions(dry_run=dry_run))
    code = DebugService().run(spec, ExecOptions(dry_run=dry_run))
    if isinstance(handle, Popen):
        handle.communicate()

    raise SystemExit(code)
