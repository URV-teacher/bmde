from __future__ import annotations

from abc import ABC

from bmde.core.backend import Backend
from ..spec import BuildSpec


class BuildBackend(Backend[BuildSpec], ABC):
    pass