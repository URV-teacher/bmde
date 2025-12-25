from __future__ import annotations

from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import BuildService
from .spec import BuildSpec

log = logging.get_logger(__name__)

def build_command(
        d: Path, arguments: Optional[list[str]], settings: Settings, dry_run: bool = False
) -> None:
    spec = BuildSpec(
        d=d,
        environment=settings.build.backend,
        entrypoint=settings.build.entrypoint,
        arguments=arguments,
        dry_run=dry_run
    )

    code = BuildService().run(spec, ExecOptions(dry_run=dry_run))
    raise SystemExit(code)
