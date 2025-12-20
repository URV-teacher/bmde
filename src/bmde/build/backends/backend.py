from __future__ import annotations

from abc import ABC

from ..spec import BuildSpec
from ...core.backend import Backend


class BuildBackend(Backend[BuildSpec], ABC):
    pass