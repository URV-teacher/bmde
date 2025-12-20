from __future__ import annotations

from pathlib import Path

from .service import BuildService
from .spec import BuildSpec
from ..config.schema import Settings
from ..core import logging
from ..core.exec import ExecOptions

log = logging.get_logger(__name__)

def build_nds_command(
        d: Path, arguments: list[str], settings: Settings, dry_run: bool = False
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
