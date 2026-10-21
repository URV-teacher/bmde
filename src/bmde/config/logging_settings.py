from pathlib import Path

from pydantic import BaseModel, Field

from bmde.core.types import LogLevel, get_default_log_path


class LoggingSettings(BaseModel):
    """Logging of the CLI."""

    level: LogLevel = Field(default=LogLevel.get_default_log_level(), description="Verbosity of the CLI output")
    file: Path | None = Field(
        default=get_default_log_path(),
        description="Path of the log file. If unset, a new timestamped file is created on each execution in the log "
        "directory of the user (~/.local/state/bmde/log on Linux)",
        json_schema_extra={"dynamic_default": "<user log directory>/<date>.log"},
    )
    hide_sensibles: bool | None = Field(default=True, description="Hide sensitive values (e.g. passwords) in the logs")
