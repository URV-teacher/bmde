from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import PatchSpec


class PatchBackend(Backend[PatchSpec], ABC):
    pass