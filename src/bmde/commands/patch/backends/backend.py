from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import PatchSpecOpts


class PatchBackend(Backend[PatchSpecOpts], ABC):
    pass
