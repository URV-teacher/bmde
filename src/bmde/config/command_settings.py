from pathlib import Path

from pydantic import BaseModel, Field

from bmde.core.types import BackendOptions


class ExecutionSettings(BaseModel):
    """How the command is executed."""

    entrypoint: Path | None = Field(
        default=None,
        description="Executable used instead of the default entrypoint of the backend",
        json_schema_extra={"advanced": True},
    )
    arguments: list[str] | None = Field(
        default=None, description="Arguments passed to the entrypoint", json_schema_extra={"advanced": True}
    )
    background: bool | None = Field(
        default=False, description="Run the command in the background", json_schema_extra={"advanced": True}
    )
    dry_run: bool | None = Field(
        default=False, description="Simulate actions without executing them", json_schema_extra={"advanced": True}
    )
    interactive: bool = Field(
        default=True, description="Run in interactive mode (allocates a TTY)", json_schema_extra={"advanced": True}
    )
    backend: BackendOptions | None = Field(
        default=None,
        description="Backend used to execute the command. If unset, the first available backend is used",
    )
