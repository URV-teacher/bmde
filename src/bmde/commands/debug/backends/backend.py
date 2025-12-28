from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import DebugSpecOpts


class DebugBackend(Backend[DebugSpecOpts], ABC):
    pass
