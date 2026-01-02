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
    InteractiveOpt,
)

log = logging.get_logger(__name__)


@app.command("git")
def git_controller(
    ctx: typer.Context,
    arguments: ArgumentsOpt = None,
    directory: DirectoryOpt = None,
    backend: BackendOpt = None,
    entrypoint: EntrypointOpt = None,
    dry_run: DryRunOpt = False,
    interactive: InteractiveOpt = True,
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

    log.trace(
        "CLI options provided:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Directory: {str(directory)}\n"
        f"- Backend: {str(backend)}\n"
        f"- Entrypoint: {str(entrypoint)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- Interactive: {str(interactive)}\n"
        f"- SSH username: {obfuscate_text(ssh_username)}\n"
        f"- SSH password: {obfuscate_text(ssh_password)}\n"
        f"- SSH host: {obfuscate_text(ssh_host)}\n"
        f"- git name: {obfuscate_text(git_name)}\n"
        f"- git email: {obfuscate_text(git_email)}\n"
        f"- VPN username: {obfuscate_text(vpn_username)}\n"
        f"- VPN password: {obfuscate_text(vpn_password)}\n"
        f"- VPN host: {obfuscate_text(vpn_host)}\n"
        f"- VPN port: {obfuscate_text(str(vpn_port))}\n"
        f"- VPN realm: {obfuscate_text(vpn_realm)}\n"
        f"- VPN cert: {obfuscate_text(vpn_cert)}\n"
        f"- VPN test DNS: {obfuscate_text(vpn_test_dns)}\n"
        f"- VPN test IP: {obfuscate_text(vpn_test_ip)}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.trace(
        "Final settings for git command:\n"
        f"- Arguments: {str(arguments)}\n"
        f"- Directory: {str(directory)}\n"
        f"- Dry run: {str(dry_run)}\n"
        f"- Interactive: {str(interactive)}\n"
        f"- Backend: {str(backend if backend is not None else settings.git.execution_settings.backend)}\n"
        f"- Entrypoint: {str(entrypoint if entrypoint is not None else settings.git.execution_settings.entrypoint)}\n"
        f"- SSH username: {obfuscate_text(ssh_username if ssh_username is not None else settings.git.ssh.username)}\n"
        f"- SSH password: {obfuscate_text(ssh_password if ssh_password is not None else settings.git.ssh.password)}\n"
        f"- SSH server: {obfuscate_text(ssh_host if ssh_host is not None else settings.git.ssh.host)}\n"
        f"- git name: {obfuscate_text(git_name if git_name is not None else settings.git.git.name)}\n"
        f"- git email: {obfuscate_text(git_email if git_email is not None else settings.git.git.email)}\n"
        f"- VPN username: {obfuscate_text(vpn_username if vpn_username is not None else settings.git.vpn.username)}\n"
        f"- VPN password: {obfuscate_text(vpn_password if vpn_password is not None else settings.git.vpn.password)}\n"
        f"- VPN host: {obfuscate_text(vpn_host if vpn_host is not None else settings.git.vpn.host)}\n"
        f"- VPN port: {obfuscate_text(str(vpn_port) if vpn_port is not None else str(settings.git.vpn.port))}\n"
        f"- VPN realm: {obfuscate_text(vpn_realm if vpn_realm is not None else settings.git.vpn.realm)}\n"
        f"- VPN cert: {obfuscate_text(vpn_cert if vpn_cert is not None else settings.git.vpn.cert)}\n"
        f"- VPN test DNS: {obfuscate_text(vpn_test_dns if vpn_test_dns is not None else settings.git.vpn.test_dns)}\n"
        f"- VPN test IP: {obfuscate_text(vpn_test_ip if vpn_test_ip is not None else settings.git.vpn.test_ip)}\n"
    )

    git_command(
        d=directory,
        arguments=arguments,
        backend=backend,
        dry_run=dry_run,
        interactive=interactive,
        entrypoint=entrypoint,
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        ssh_host=ssh_host,
        git_name=git_name,
        git_email=git_email,
        vpn_username=vpn_username,
        vpn_password=vpn_password,
        vpn_host=vpn_host,
        vpn_port=vpn_port,
        vpn_realm=vpn_realm,
        vpn_cert=vpn_cert,
        vpn_test_dns=vpn_test_dns,
        vpn_test_ip=vpn_test_ip,
        settings=settings.git,
    )
