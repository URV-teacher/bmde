from pathlib import Path

from pydantic import BaseModel

from bmde.core.types import LogLevel, get_default_log_path


class LoggingSettings(BaseModel):
    level: LogLevel = LogLevel.get_default_log_level()
    file: Path | None = get_default_log_path()
    hide_sensibles: bool | None = True
