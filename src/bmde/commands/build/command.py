from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import BuildService
from .spec import BuildSpec

log = logging.get_logger(__name__)

def build_command(
        d: Optional[Path], arguments: Optional[list[str]], settings: Settings, dry_run: bool = False
) -> None:

    if d is None:
        d = Path(os.getcwd())

    spec = BuildSpec(
        d=d,
        backend=settings.build.backend,
        entrypoint=settings.build.execution_settings.entrypoint,
        arguments=arguments,
        dry_run=dry_run
    )

    code = BuildService().run(spec, ExecOptions(dry_run=dry_run))
    raise SystemExit(code)
