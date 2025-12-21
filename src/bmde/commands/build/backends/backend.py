from __future__ import annotations

from abc import ABC

from ..spec import BuildSpec
from bmde.core.backend import Backend


class BuildBackend(Backend[BuildSpec], ABC):
    pass