from pydantic import BaseModel, Field


class DockerSettings(BaseModel):
    """Docker images of the "docker" backend of every command."""

    image_tag: str | None = Field(
        default=None,
        description="Tag of the Docker images of the tools, to pin a known-good environment (e.g. 1.15.0 or "
        "sha-<commit>). If unset, the images published with the installed version of bmde, or latest for a "
        "development version",
        json_schema_extra={"dynamic_default": "<version of bmde>"},
    )
