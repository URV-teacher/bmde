from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import PatchSpec
from ...core.backend import Backend
from ...core.exec import ExecOptions


class PatchBackend(Backend[PatchSpec], ABC):
    pass