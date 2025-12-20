from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Dict

from ..build.backends.docker import DockerRunner
from ..build.backends.host import HostRunner
from ..build.spec import BuildSpec
from ..core import logging
from ..core.exec import ExecOptions

log = logging.get_logger(__name__)

SpecType = TypeVar("SpecType")  # will be GitSpec, BuildSpec, etc.
BackendType = TypeVar("BackendType")  # will be BuildBackend, RunBackend, etc.

class Service(Generic[SpecType, BackendType], ABC):
    
    def __init__(self, order: List[str], mapping: Dict[str, BackendType]) -> None:
        self.order = order
        self.mapping = mapping

    def choose_backend(self, env: str | None) -> list:
        order = self.order
        if env:
            order = [env]  # force
        return [self.mapping[e] for e in order]

    def run(self, spec: SpecType, exec_opts: ExecOptions) -> int:
        for backend in self.choose_backend(spec.environment):
            if backend.is_available():
                return backend.run(spec, exec_opts)
        raise RuntimeError("No suitable backend available")

