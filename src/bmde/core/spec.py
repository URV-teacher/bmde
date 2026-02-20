from abc import ABC

from bmde.core.types import BackendOptions


class BaseSpec(ABC):
    backend: BackendOptions | None
