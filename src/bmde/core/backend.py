from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from bmde.core.exec import ExecOptions
from bmde.core.spec import BaseSpec

SpecType = TypeVar("SpecType", bound=BaseSpec)  # will be GitSpec, BuildSpec, etc.


class Backend(ABC, Generic[SpecType]):
    """
    Generic interface for backends. Each runner backend must implement a function to use it and to determine if it
    is available.
    """

    @abstractmethod
    def is_available(self) -> bool: ...

    def check(self) -> bool:
        """
        Performs detailed checks to verify if the backend is correctly configured.
        Returns True if all checks pass, False otherwise.
        Default implementation returns True.
        """
        return True

    @abstractmethod
    def run(
        self, spec: SpecType, exec_opts: ExecOptions
    ) -> int | subprocess.Popen[bytes]: ...
