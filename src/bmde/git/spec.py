from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Literal

from bmde.core.types import Backend, BackendName


@dataclass
class GitSpec:
    d: Path
    environment: Optional[BackendName]
    entrypoint: Optional[str]
    arguments: Sequence[str]
    shell: bool
    dry_run: bool

    ssh_username: str      # TODO: Use more restrictive typing for these args
    ssh_password: str
    ssh_host: str

    git_name: str
    git_email: str

    vpn_username: str
    vpn_password: str
    vpn_host: str
    vpn_port: int
    vpn_realm: str
    vpn_cert: str
    vpn_test_dns: str
    vpn_test_ip: str


