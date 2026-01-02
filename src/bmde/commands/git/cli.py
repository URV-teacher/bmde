import typer

from bmde.cli import app
from bmde.commands.git.command import git_command
from bmde.config.schema import Settings
from bmde.core import logging
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
        f"- SSH username: {ssh_username}\n"
        f"- SSH password: {ssh_password}\n"
        f"- SSH host: {ssh_host}\n"
        f"- git name: {git_name}\n"
        f"- git email: {git_email}\n"
        f"- VPN username: {vpn_username}\n"
        f"- VPN password: {vpn_password}\n"
        f"- VPN host: {vpn_host}\n"
        f"- VPN port: {str(vpn_port)}\n"
        f"- VPN realm: {vpn_realm}\n"
        f"- VPN cert: {vpn_cert}\n"
        f"- VPN test DNS: {vpn_test_dns}\n"
        f"- VPN test IP: {vpn_test_ip}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.trace("Final settings for git command:\n" f"- {str(settings.git)}\n")

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
