from typing import Optional

from pydantic import BaseModel

from bmde.config.command_settings import ExecutionSettings


class VpnAuthSettings(BaseModel):
    enabled: bool = True
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    cert: Optional[str] = None
    realm: Optional[str] = None
    test_dns: Optional[str] = None
    test_ip: Optional[str] = None


class GitSshSettings(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None


class GitConfigSettings(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class GitSettings(BaseModel):
    execution_settings: ExecutionSettings = ExecutionSettings()

    git: GitConfigSettings = GitConfigSettings()
    ssh: GitSshSettings = GitSshSettings()
    vpn: VpnAuthSettings = VpnAuthSettings()
