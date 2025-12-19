from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import BuildSpec
from ...core.exec import ExecOptions
from ...core.backend import Backend


class BuildBackend(Backend[BuildSpec], ABC):
    pass