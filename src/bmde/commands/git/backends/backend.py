from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import GitSpec


class GitBackend(Backend[GitSpec], ABC):
    pass