from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import BuildService
from .spec import BuildSpec, BuildSpecOpts
from ...core.spec_opts import SpecExecOpts

log = logging.get_logger(__name__)

def build_command(
        d: Optional[Path], arguments: Optional[list[str]], settings: Settings, dry_run: bool = False
) -> None:

    if d is None:
        d = Path(os.getcwd())

    spec = BuildSpec(
        BuildSpecOpts=BuildSpecOpts(
            d=d,
        ),
        SpecExecOpts=SpecExecOpts(
            backend=settings.build.backend,
            entrypoint=settings.build.execution_settings.entrypoint,
            arguments=arguments,
            dry_run=dry_run,
            background=settings.build.execution_settings.background,
        )
    )

    code = BuildService().run(spec, ExecOptions(dry_run=dry_run))
    raise SystemExit(code)
