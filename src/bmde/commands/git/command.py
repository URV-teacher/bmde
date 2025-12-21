from __future__ import annotations

from pathlib import Path
from typing import Optional

from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import GitService
from .spec import GitSpec

log = logging.get_logger(__name__)

def git_command(
        d: Path, arguments: Optional[tuple[str]], settings: Settings, dry_run: bool = False
) -> int:
    spec = GitSpec(
        d=d,
        environment=settings.git.backend,
        entrypoint=settings.git.entrypoint,
        arguments=arguments,
        dry_run=dry_run,

        ssh_username=settings.git.ssh.username,
        ssh_password=settings.git.ssh.password,
        ssh_host=settings.git.ssh.host,

        git_name=settings.git.git.name,
        git_email=settings.git.git.email,

        vpn_username=settings.git.vpn.username,
        vpn_password=settings.git.vpn.password,
        vpn_host=settings.git.vpn.host,
        vpn_port=settings.git.vpn.port,
        vpn_realm=settings.git.vpn.realm,
        vpn_cert=settings.git.vpn.cert,
        vpn_test_dns=settings.git.vpn.test_dns,
        vpn_test_ip=settings.git.vpn.test_ip
    )
    return GitService().run(spec, ExecOptions(dry_run=dry_run))
