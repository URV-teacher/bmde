import os
from pathlib import Path

import typer

from bmde.cli import app
from bmde.commands.git.command import git_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.logging import obfuscate_text
from bmde.core.shared_options import (
    ArgumentsOpt,
    DirectoryOpt,
    BackendOpt,
    EntrypointOpt,
    DryRunOpt,
    SshUsernameOpt,
    SshPasswordOpt,
    SshHostOpt,
    GitNameOpt,
    GitEmailOpt,
    VpnUsernameOpt,
    VpnPasswordOpt,
    VpnHostOpt,
    VpnPortOpt,
    VpnRealmOpt,
    VpnCertOpt,
    VpnTestDnsOpt,
    VpnTestIpOpt,
)

log = logging.get_logger(__name__)


@app.command("git")
def git_controller(
    ctx: typer.Context,
    arguments: ArgumentsOpt = None,
    directory: DirectoryOpt = Path(os.getcwd()),
    backend: BackendOpt = None,
    entrypoint: EntrypointOpt = None,
    dry_run: DryRunOpt = False,
    ssh_username: SshUsernameOpt = None,
    ssh_password: SshPasswordOpt = None,
    ssh_host: SshHostOpt = None,
    git_name: GitNameOpt = None,
    git_email: GitEmailOpt = None,
    vpn_username: VpnUsernameOpt = None,
    vpn_password: VpnPasswordOpt = None,
    vpn_host: VpnHostOpt = None,
    vpn_port: VpnPortOpt = None,
    vpn_realm: VpnRealmOpt = None,
    vpn_cert: VpnCertOpt = None,
    vpn_test_dns: VpnTestDnsOpt = None,
    vpn_test_ip: VpnTestIpOpt = None,
) -> None:
    """git wrapper with SSH password bypass and VPN management. git is a distributed version control system."""

    settings: Settings = ctx.obj["settings"]

    log.trace(
        "CLI options provided:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Directory: {str(directory)}\n"
        f"- Backend: {str(backend)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- SSH username: {obfuscate_text(ssh_username)}\n"
        f"- SSH password: {obfuscate_text(ssh_password)}\n"
        f"- SSH host: {obfuscate_text(ssh_host)}\n"
        f"- git name: {obfuscate_text(git_name)}\n"
        f"- git email: {obfuscate_text(git_email)}\n"
        f"- VPN username: {obfuscate_text(vpn_username)}\n"
        f"- VPN password: {obfuscate_text(vpn_password)}\n"
        f"- VPN host: {obfuscate_text(vpn_host)}\n"
        f"- VPN port: {obfuscate_text(vpn_port)}\n"
        f"- VPN realm: {obfuscate_text(vpn_realm)}\n"
        f"- VPN cert: {obfuscate_text(vpn_cert)}\n"
        f"- VPN test DNS: {obfuscate_text(vpn_test_dns)}\n"
        f"- VPN test IP: {obfuscate_text(vpn_test_ip)}\n"
    )

    # CLI overrides
    if backend is not None:
        settings.git.backend = backend
    if entrypoint is not None:
        settings.git.entrypoint = entrypoint

    if ssh_username is not None:
        settings.git.ssh.username = ssh_username
    if ssh_password is not None:
        settings.git.ssh.password = ssh_password
    if ssh_host is not None:
        settings.git.ssh.host = ssh_host

    if git_name is not None:
        settings.git.git.name = git_name
    if git_email is not None:
        settings.git.git.email = git_email

    if vpn_username is not None:
        settings.git.vpn.username = vpn_username
    if vpn_password is not None:
        settings.git.vpn.password = vpn_password
    if vpn_host is not None:
        settings.git.vpn.host = vpn_host
    if vpn_realm is not None:
        settings.git.vpn.realm = vpn_realm
    if vpn_cert is not None:
        settings.git.vpn.cert = vpn_cert
    if vpn_test_dns is not None:
        settings.git.vpn.test_dns = vpn_test_dns
    if vpn_test_ip is not None:
        settings.git.vpn.test_ip = vpn_test_ip

    log.trace(
        "Final settings for git command:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Directory: {str(directory)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- Backend: {str(settings.git.backend)}\n"
        f"- Entrypoint: {str(settings.git.entrypoint)}\n"
        f"- SSH username: {obfuscate_text(settings.git.ssh.username)}\n"
        f"- SSH password: {obfuscate_text(settings.git.ssh.password)}\n"
        f"- SSH server: {obfuscate_text(settings.git.ssh.host)}\n"
        f"- git name: {obfuscate_text(settings.git.git.name)}\n"
        f"- git email: {obfuscate_text(settings.git.git.email)}\n"
        f"- VPN username: {obfuscate_text(settings.git.vpn.username)}\n"
        f"- VPN password: {obfuscate_text(settings.git.vpn.password)}\n"
        f"- VPN host: {obfuscate_text(settings.git.vpn.host)}\n"
        f"- VPN port: {obfuscate_text(str(settings.git.vpn.port))}\n"
        f"- VPN realm: {obfuscate_text(settings.git.vpn.realm)}\n"
        f"- VPN cert: {obfuscate_text(settings.git.vpn.cert)}\n"
        f"- VPN test DNS: {obfuscate_text(settings.git.vpn.test_dns)}\n"
        f"- VPN test IP: {obfuscate_text(settings.git.vpn.test_ip)}\n"
    )

    git_command(d=directory, arguments=arguments, settings=settings, dry_run=dry_run)
