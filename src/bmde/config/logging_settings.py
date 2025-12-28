from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from bmde.core.logging import LogLevel, get_default_log_path


class LoggingSettings(BaseModel):
    level: LogLevel = LogLevel("info")
    file: Optional[Path] = get_default_log_path()
