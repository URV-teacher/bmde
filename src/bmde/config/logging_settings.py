from typing import Optional

from pydantic import BaseModel, FilePath

from bmde.core.logging import LogLevel


class LoggingSettings(BaseModel):
    level: LogLevel = LogLevel("info")
    file: Optional[FilePath] = None
