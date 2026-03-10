from __future__ import annotations

import subprocess
from abc import ABC
from subprocess import Popen
from typing import Any, Generic, TypeVar

from ..core import logging
from ..core.exec import ExecOptions
from .backend import Backend
from .spec import BaseSpec
from .types import BackendOptions

log = logging.get_logger(__name__)

SpecType = TypeVar("SpecType", bound=BaseSpec)  # will be GitSpec, BuildSpec, etc.
BackendType = TypeVar(
    "BackendType", bound=Backend[Any], covariant=True
)  # will be BuildBackend, RunBackend, etc.


class Service(Generic[SpecType, BackendType], ABC):

    def __init__(
        self,
        order: list[BackendOptions | BackendOptions],
        mapping: dict[BackendOptions | BackendOptions, BackendType],
    ) -> None:
        # We should use Any for a good generic class, but I prefer to break inheritance and restrict certain types
        # because I can not use a parent, since Enums are final (RunBackendOptions and BackendOptions
        self.order = order
        self.mapping = mapping

    def choose_backend(
        self, env: BackendOptions | BackendOptions | None
    ) -> list[BackendType]:
        order = self.order
        if env:
            order = [env]  # force
        return [self.mapping[e] for e in order]

    def run(self, spec: SpecType, exec_opts: ExecOptions) -> int | Popen[bytes]:
        for backend in self.choose_backend(exec_opts.backend):
            if backend.is_available():
                ret = backend.run(spec, exec_opts)
                # Use isinstance for type narrowing
                if isinstance(ret, (int, subprocess.Popen)):
                    return ret
                    # returncode is guaranteed to be an int after communicate()
        raise RuntimeError("No suitable backend available")
