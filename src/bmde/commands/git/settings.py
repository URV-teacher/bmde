from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings


class VpnAuthSettings(BaseModel):
    enabled: bool = True
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None
    cert: str | None = None
    realm: str | None = None
    test_dns: str | None = None
    test_ip: str | None = None


class GitSshSettings(BaseModel):
    username: str | None = None
    password: str | None = None
    host: str | None = None


class GitConfigSettings(BaseModel):
    name: str | None = None
    email: str | None = None


class GitSettings(BaseModel):
    execution_settings: ExecutionSettings = ExecutionSettings()

    git: GitConfigSettings = GitConfigSettings()
    ssh: GitSshSettings = GitSshSettings()
    vpn: VpnAuthSettings = VpnAuthSettings()
