from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bmde.core.spec import BaseSpec
from bmde.core.types import BackendOptions


@dataclass
class GitSpec(BaseSpec):
    d: Path
    environment: Optional[BackendOptions]
    entrypoint: Optional[Path]
    arguments: Optional[tuple[str]]
    dry_run: bool

    ssh_username: Optional[str]      # TODO: Use more restrictive typing for these args
    ssh_password: Optional[str]
    ssh_host: Optional[str]

    git_name: Optional[str]
    git_email: Optional[str]

    vpn_username: Optional[str]
    vpn_password: Optional[str]
    vpn_host: Optional[str]
    vpn_port: Optional[int]
    vpn_realm: Optional[str]
    vpn_cert: Optional[str]
    vpn_test_dns: Optional[str]
    vpn_test_ip: Optional[str]


