import typer

from bmde.commands.git.command import git_command
from bmde.config.schema import Settings
from bmde.core import logging
from bmde.core.logging import obfuscate_text
from bmde.core.shared_options import (
    ArgumentsOpt,
    BackendOpt,
    DirectoryOpt,
    DryRunOpt,
    EntrypointOpt,
    GitEmailOpt,
    GitNameOpt,
    InteractiveOpt,
    SshHostOpt,
    SshPasswordOpt,
    SshUsernameOpt,
    VpnCertOpt,
    VpnHostOpt,
    VpnOpt,
    VpnPasswordOpt,
    VpnPortOpt,
    VpnRealmOpt,
    VpnTestDnsOpt,
    VpnTestIpOpt,
    VpnUsernameOpt,
)

log = logging.get_logger(__name__)


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
    vpn_enabled: VpnOpt = None,
) -> None:
    """Git wrapper with SSH password bypass and VPN management. git is a distributed version control system."""
    log.trace(
        "CLI options provided:\n"
        f"- Arguments: {arguments!s}\n"
        f"- Directory: {directory!s}\n"
        f"- Backend: {backend!s}\n"
        f"- Entrypoint: {entrypoint!s}\n"
        f"- Dry run: {dry_run!s}\n"
        f"- Interactive: {interactive!s}\n"
        f"- SSH username: {ssh_username}\n"
        f"- SSH password: {obfuscate_text(ssh_password)}\n"
        f"- SSH host: {ssh_host}\n"
        f"- git name: {git_name}\n"
        f"- git email: {git_email}\n"
        f"- VPN username: {vpn_username}\n"
        f"- VPN password: {obfuscate_text(vpn_password)}\n"
        f"- VPN host: {vpn_host}\n"
        f"- VPN port: {vpn_port!s}\n"
        f"- VPN realm: {vpn_realm}\n"
        f"- VPN cert: {vpn_cert}\n"
        f"- VPN test DNS: {vpn_test_dns}\n"
        f"- VPN test IP: {vpn_test_ip}\n"
    )

    settings: Settings = ctx.obj["settings"]

    log.trace(f"Final settings for git command:\n- {settings.git!s}\n")

    ret = git_command(
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
        vpn_enabled=vpn_enabled,
        settings=settings.git,
    )

    if isinstance(ret, int):
        raise typer.Exit(ret)
