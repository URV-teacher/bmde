from __future__ import annotations

from pathlib import Path

from .service import run
from .spec import PatchSpec
from ..config.schema import Settings
from ..core import logging
from ..core.exec import ExecOptions

log = logging.get_logger(__name__)

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
