from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import PatchService
from .spec import PatchSpec

log = logging.get_logger(__name__)


def patch_command(
    d: Optional[Path],
    arguments: Optional[list[str]],
    settings: Settings,
    dry_run: bool = False,
) -> None:
    spec = PatchSpec(
        d=d if d is not None else Path(os.getcwd()),
        backend=settings.patch.backend,
        entrypoint=settings.patch.execution_settings.entrypoint,
        arguments=arguments,
        dry_run=dry_run,
    )
    code = PatchService().run(spec, ExecOptions(dry_run=dry_run))
    raise SystemExit(code)
