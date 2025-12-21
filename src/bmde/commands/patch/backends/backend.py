from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import PatchSpec
from bmde.core.backend import Backend
from bmde.core.exec import ExecOptions


class PatchBackend(Backend[PatchSpec], ABC):
    pass