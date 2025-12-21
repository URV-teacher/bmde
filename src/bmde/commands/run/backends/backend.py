from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import RunSpec
from bmde.core.backend import Backend
from bmde.core.exec import ExecOptions


class RunBackend(Backend[RunSpec], ABC):
    pass