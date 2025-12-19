from __future__ import annotations

import logging

from .backends.docker import DockerRunner
from .backends.host import HostRunner
from .spec import PatchSpec
from ..core.exec import ExecOptions

log = logging.getLogger(__name__)


def choose_backend(env: str | None) -> list:
    order = ["host", "docker"]
    if env:
        order = [env]  # force
    mapping = {"host": HostRunner(), "docker": DockerRunner()}
    return [mapping[e] for e in order]

def run(spec: PatchSpec, exec_opts: ExecOptions) -> int:
    for backend in choose_backend(spec.environment):
        if backend.is_available():
            return backend.run(spec, exec_opts)
    raise RuntimeError("No suitable backend available")
