from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import BuildSpec
from ...core.exec import ExecOptions


class BuildBackend(ABC):
    """
    Interface for the strategy pattern. Each runner backend must implement a function to use it and to determine if it
    is available.
    """
    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def run(self, spec: BuildSpec, exec_opts: ExecOptions) -> int: ...
