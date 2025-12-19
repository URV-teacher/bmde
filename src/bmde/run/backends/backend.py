from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import RunSpec
from ...core.backend import Backend
from ...core.exec import ExecOptions


class RunBackend(Backend[RunSpec], ABC):
    pass