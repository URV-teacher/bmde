from abc import ABC
from typing import Optional

from bmde.core.types import BackendOptions


class BaseSpec(ABC):
    backend: Optional[BackendOptions]
