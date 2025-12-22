from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import DebugSpec


class DebugBackend(Backend[DebugSpec], ABC):
    pass
