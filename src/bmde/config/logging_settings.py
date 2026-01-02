from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from bmde.core.types import LogLevel, get_default_log_path


class LoggingSettings(BaseModel):
    level: LogLevel = LogLevel.get_default_log_level()
    file: Optional[Path] = get_default_log_path()
    hide_sensibles: Optional[bool] = True
