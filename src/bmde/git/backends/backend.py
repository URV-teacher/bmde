from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import GitSpec
from ...core.backend import Backend
from ...core.exec import ExecOptions


class GitBackend(Backend[GitSpec], ABC):
    pass