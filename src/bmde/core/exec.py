from __future__ import annotations

import subprocess
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path

from bmde.core import logging
from bmde.core.types import BackendOptions

log = logging.get_logger(__name__)


@dataclass
class ExecOptions:
    dry_run: bool | None | None = False
    env: dict[str, str] | None = None
    cwd: str | None = None
    background: bool | None = False
    interactive: bool = True
    backend: BackendOptions | None = None
    entrypoint: Path | None = None
    arguments: list[str] | None = None
    # File where stdout and stderr are written instead of the terminal
    log_file: Path | None = None


def run_cmd(cmd: list[str], opts: ExecOptions) -> int | subprocess.Popen[bytes]:
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

    # The child process keeps its own copy of the file descriptor, so the file can be closed right after starting it
    with ExitStack() as stack:
        log_file = stack.enter_context(open(opts.log_file, "wb")) if opts.log_file is not None else None
        stderr = subprocess.STDOUT if log_file is not None else None
        result: int | subprocess.Popen[bytes]
        if opts.background:
            # Non-blocking execution, the caller can manage the process
            result = subprocess.Popen(args, env=opts.env, cwd=opts.cwd, stdout=log_file, stderr=stderr)
        else:
            result = subprocess.call(
                args, env=opts.env, cwd=opts.cwd, stdout=log_file, stderr=stderr
            )  # no shell injection risk
    return result
