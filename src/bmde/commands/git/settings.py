from pydantic import BaseModel, Field

from bmde.config.command_settings import ExecutionSettings


class VpnAuthSettings(BaseModel):
    """VPN (forticlient) used to reach the git server."""

    enabled: bool = Field(default=True, description="Connect to the VPN before running git")
    username: str | None = Field(default=None, description="User name for forticlient authentication")
    password: str | None = Field(
        default=None, description="User password for forticlient authentication", json_schema_extra={"secret": True}
    )
    host: str | None = Field(default=None, description="VPN gateway for forticlient")
    port: int | None = Field(default=None, description="VPN port for forticlient")
    cert: str | None = Field(default=None, description="VPN cert for forticlient")
    realm: str | None = Field(default=None, description="VPN realm for forticlient")
    test_dns: str | None = Field(
        default=None, description="DNS name requested to validate that the internal network is reachable"
    )
    test_ip: str | None = Field(
        default=None, description="IP address requested to validate that the internal network is reachable"
    )


class GitSshSettings(BaseModel):
    """SSH authentication of git."""

    username: str | None = Field(default=None, description="User name for the SSH authentication of git")
    password: str | None = Field(
        default=None,
        description="User password for the SSH authentication of git",
        json_schema_extra={"secret": True},
    )
    host: str | None = Field(default=None, description="Hostname of the SSH server")


class GitConfigSettings(BaseModel):
    """Identity used in the git commits."""

    name: str | None = Field(default=None, description="User name for git commit signature")
    email: str | None = Field(default=None, description="User email for git commit signature")


class GitSettings(BaseModel):
    """Settings of the git command."""

    execution_settings: ExecutionSettings = ExecutionSettings()

    git: GitConfigSettings = GitConfigSettings()
    ssh: GitSshSettings = GitSshSettings()
    vpn: VpnAuthSettings = VpnAuthSettings()
