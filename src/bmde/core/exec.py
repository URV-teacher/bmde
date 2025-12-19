from __future__ import annotations

import subprocess
from dataclasses import dataclass

from bmde.core import logging

log = logging.get_logger(__name__)


@dataclass
class ExecOptions:
    dry_run: bool = False
    env: dict | None = None
    cwd: str | None = None


def run_cmd(cmd: list[str] | str, opts: ExecOptions) -> int:
    if isinstance(cmd, str):
        pretty = cmd
        args = cmd
    else:
        pretty = " ".join(cmd)
        args = cmd

    log.trace("exec: %s", pretty)
    if opts.dry_run:
        log.info("[dry-run] %s", pretty)
        return 0
    return subprocess.call(args, env=opts.env, cwd=opts.cwd)  # no shell injection risk
