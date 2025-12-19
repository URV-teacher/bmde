from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import GitSpec
from ...core.exec import ExecOptions


class GitBackend(ABC):
    """
    Interface for the strategy pattern. Each runner backend must implement a function to use it and to determine if it
    is available.
    """
    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def run(self, spec: GitSpec, exec_opts: ExecOptions) -> int: ...
