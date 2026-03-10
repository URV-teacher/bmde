from dataclasses import dataclass
from pathlib import Path

from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts


@dataclass
class GitSpecOpts(BaseSpec):
    d: Path
    ssh_username: str | None
    ssh_password: str | None
    ssh_host: str | None
    git_name: str | None
    git_email: str | None
    vpn_username: str | None
    vpn_password: str | None
    vpn_host: str | None
    vpn_port: int | None
    vpn_realm: str | None
    vpn_cert: str | None
    vpn_test_dns: str | None
    vpn_test_ip: str | None


@dataclass
class GitSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    GitSpecOpts: GitSpecOpts
