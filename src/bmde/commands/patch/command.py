from __future__ import annotations

from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import PatchService
from .spec import PatchSpec

log = logging.get_logger(__name__)


def patch_command(
    d: Path, arguments: Optional[tuple[str]], settings: Settings, dry_run: bool = False
) -> None:
    spec = PatchSpec(
        d=d,
        environment=settings.patch.backend,
        entrypoint=settings.patch.entrypoint,
        arguments=arguments,
        dry_run=dry_run,
    )
    code = PatchService().run(spec, ExecOptions(dry_run=dry_run))
    raise SystemExit(code)
