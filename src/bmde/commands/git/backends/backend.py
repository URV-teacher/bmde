from __future__ import annotations
from abc import ABC, abstractmethod
from ..spec import GitSpec
from bmde.core.backend import Backend
from bmde.core.exec import ExecOptions


class GitBackend(Backend[GitSpec], ABC):
    pass