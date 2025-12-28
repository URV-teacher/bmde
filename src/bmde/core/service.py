from __future__ import annotations

import subprocess
from abc import ABC
from subprocess import Popen
from typing import List, TypeVar, Generic, Dict, Any

from .backend import Backend
from .spec import BaseSpec
from .types import RunBackendOptions, BackendOptions
from ..core import logging
from ..core.exec import ExecOptions

log = logging.get_logger(__name__)

SpecType = TypeVar("SpecType", bound=BaseSpec)  # will be GitSpec, BuildSpec, etc.
BackendType = TypeVar(
    "BackendType", bound=Backend[Any], covariant=True
)  # will be BuildBackend, RunBackend, etc.


class Service(Generic[SpecType, BackendType], ABC):

    def __init__(
        self,
        order: List[RunBackendOptions | BackendOptions],
        mapping: Dict[RunBackendOptions | BackendOptions, BackendType],
    ) -> None:
        # We should use Any for a good generic class, but I prefer to break inheritance and restrict certain types
        # because I can not use a parent, since Enums are final (RunBackendOptions and BackendOptions
        self.order = order
        self.mapping = mapping

    def choose_backend(
        self, env: RunBackendOptions | BackendOptions | None
    ) -> list[BackendType]:
        order = self.order
        if env:
            order = [env]  # force
        return [self.mapping[e] for e in order]

    def run(self, spec: SpecType, exec_opts: ExecOptions) -> int | Popen[bytes]:
        for backend in self.choose_backend(spec.backend):
            if backend.is_available():
                ret = backend.run(spec, exec_opts)
                # Use isinstance for type narrowing
                if isinstance(ret, int):
                    return ret

                # Use the base class for isinstance; generic [bytes]
                # does not exist at runtime (type erasure)
                elif isinstance(ret, subprocess.Popen):
                    return ret
                    # returncode is guaranteed to be an int after communicate()
        raise RuntimeError("No suitable backend available")
