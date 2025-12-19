from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import RunSpec
from ...core.exec import ExecOptions


class RunnerBackend(ABC):
    """
    Interface for the strategy pattern. Each runner backend must implement a function to use it and to determine if it
    is available.
    """
    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def run(self, spec: RunSpec, exec_opts: ExecOptions) -> int: ...
