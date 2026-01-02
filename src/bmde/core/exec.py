from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core import logging
from bmde.core.types import BackendOptions

log = logging.get_logger(__name__)


@dataclass
class ExecOptions:
    dry_run: Optional[bool] | None = False
    env: Optional[dict[str, str]] = None
    cwd: Optional[str] = None
    background: Optional[bool] = False
    interactive: bool = True
    backend: Optional[BackendOptions] = None
    entrypoint: Optional[Path] = None
    arguments: Optional[list[str]] = None


def run_cmd(cmd: list[str], opts: ExecOptions) -> int | subprocess.Popen[bytes]:
    if isinstance(cmd, str):
        pretty = cmd
        args = cmd
    else:
        pretty = " ".join(cmd)
        args = cmd

    log.debug("exec: %s", pretty)
    if opts.dry_run:
        log.info("[dry-run] %s", pretty)
        return 0

    if opts.background:
        # Non-blocking execution
        proc = subprocess.Popen(
            args,
            env=opts.env,
            cwd=opts.cwd,
        )
        return proc  # caller can manage it
    else:
        return subprocess.call(
            args, env=opts.env, cwd=opts.cwd
        )  # no shell injection risk
