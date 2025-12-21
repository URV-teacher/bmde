from abc import ABC
from typing import Optional

from bmde.core.types import BackendOptions, RunBackendOptions


class BaseSpec(ABC):
    environment: Optional[BackendOptions | RunBackendOptions]