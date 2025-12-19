from __future__ import annotations

from pathlib import Path

from .service import run
from .spec import GitSpec
from ..config.schema import Settings
from ..core import logging
from ..core.exec import ExecOptions

log = logging.get_logger(__name__)

def git_nds_command(
        d: Path, shell: bool, arguments: list[str], settings: Settings, dry_run: bool = False
) -> int:
    spec = GitSpec(
        d=d,
        environment=settings.git.backend,
        entrypoint=settings.git.entrypoint,
        arguments=arguments,
        shell=shell,
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
    return run(spec, ExecOptions(dry_run=dry_run))
