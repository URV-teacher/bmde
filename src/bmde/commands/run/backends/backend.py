from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import RunSpec


class RunBackend(Backend[RunSpec], ABC):
    pass