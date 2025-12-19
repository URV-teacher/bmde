# src/bmde/run/command.py
from __future__ import annotations

import logging
from pathlib import Path

from .service import run
from .spec import PatchSpec
from ..config.schema import Settings
from ..core.exec import ExecOptions
from ..core.logging import setup_logging

log = logging.getLogger("bmde.patch")

def patch_nds_command(
        d: Path, shell: bool, arguments: list[str], settings: Settings, dry_run: bool = False
) -> None:
    spec = PatchSpec(
        d=d,
        environment=settings.patch.backend,
        entrypoint=settings.patch.entrypoint,
        arguments=arguments,
        shell=shell,
        dry_run=dry_run
    )
    code = run(spec, ExecOptions(dry_run=dry_run))
    raise SystemExit(code)
