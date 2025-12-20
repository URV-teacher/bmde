"""
The responsibility of this file is to implement the functions that will be called when calling each subcommand in the
CLI. Each function is responsible for attending a single subcommand with their arguments specified through the function
typehint arguments using Typer. Each function will build a Settings object with the CLI overrides, arguments and default
settings, which will be passed to the function and run a command.
Each function will also be responsible for aborting execution with CLI arguments that are impossible. This only applies
to data coming from the CLI, the syntax of the overrides is not responsibility of the function of these files.
"""

# Debug
from __future__ import annotations

import os

import typer
from pygments.lexers import shell
from rich.console import Console

from .build.command import build_command
from .config.loader import load_settings
from .config.schema import Settings
from .core import logging
from .core.logging import setup_logging, get_default_log_path
from .core.types import LogLevel
from .git.command import git_command
from .patch.command import patch_command
from .run.command import run_command
from .shared_options import (
    RunBackendOpt, EntrypointOpt, DebugOpt, PortOpt,
    DryRunOpt, VerboseOpt, QuietOpt, DockerScreenOpt, BackendOpt, ArgumentsOpt, DirectoryOpt,
    VeryVerboseOpt, VeryQuietOpt, LogFileOpt, NdsRomOpt, FatImageOpt, SshUsernameOpt,
    VpnCertOpt, VpnTestDnsOpt, VpnTestIpOpt, VpnPortOpt, VpnRealmOpt, VpnHostOpt, VpnPasswordOpt, VpnUsernameOpt,
    GitEmailOpt, GitNameOpt, SshPasswordOpt, SshHostOpt, ConfigOpt
)

console = Console()
app = typer.Typer(add_completion=False, help="BMDE CLI", no_args_is_help=True)  # TODO Completion does not work
log = logging.get_logger(__name__)



@app.callback()
def _global(ctx: typer.Context,
            config: ConfigOpt = None,
            verbose: VerboseOpt = False,
            very_verbose: VeryVerboseOpt = False,
            quiet: QuietOpt = False,
            very_quiet: VeryQuietOpt = False,
            log_file: LogFileOpt = None,
            ):
    """
    Global option callback. Executed if no command is provided.
    """
    # Preventive creation of logger if CLI options are provided before loading settings
    if very_verbose is True:
        log_level = LogLevel.TRACE
    elif verbose is True:
        log_level = LogLevel.DEBUG
    elif quiet is True:
        log_level = LogLevel.WARNING
    elif very_quiet is True:
        log_level = LogLevel.QUIET
    else:
        log_level = LogLevel.INFO

    if log_level is not None:
        preventive_log_level = log_level.to_logging_level()
    else:
        preventive_log_level = LogLevel.INFO.to_logging_level()  # Default if no CLI option specified

    if log_file is None:
        preventive_log_file = get_default_log_path()
    else:
        preventive_log_file = log_file

    setup_logging(preventive_log_level, log_file=preventive_log_file)  # Preventive creation of log for logging the loading of settings

    flag_counter = 0
    for flag in (very_verbose, verbose, quiet, very_quiet):
        if flag is True:
            flag_counter += 1
    if flag_counter > 1:
        log.warning("You can not use more than one verbosity flag at the same time. The most verbose flag you specified "
                    "will be applied.")
    # Load settings
    settings = load_settings(explicit_config=config)

    # CLI overrides
    if log_file is not None:
        settings.logging.log_file = log_file
    if log_level is not None:  # CLI specifies a logging level
        settings.logging.level = log_level

    # Global logging setup
    setup_logging(LogLevel(settings.logging.level).to_logging_level(), log_file=settings.logging.file)

    # Load settings into global context
    ctx.obj = {"settings": settings}


@app.command("run")
def run_controller(
    ctx: typer.Context,
    nds: NdsRomOpt = None,
    image: FatImageOpt = None,
    arguments: ArgumentsOpt = (),
    docker_screen: DockerScreenOpt = None,
    # common flags
    backend: RunBackendOpt = None,
    entrypoint: EntrypointOpt = None,
    debug: DebugOpt = False,
    port: PortOpt = 1000,
    dry_run: DryRunOpt = False,
):
    """desmume wrapper. Runs an NDS ROM."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Docker screen: {str(docker_screen)}\n"
              f"- NDS ROM: {str(nds)}\n"
              )

    # CLI overrides
    if backend is not None:
        settings.run.backend = backend
    if entrypoint is not None:
        settings.run.entrypoint = entrypoint
    if debug:
        settings.run.debug = True
    if port:
        settings.run.port = port
    if docker_screen:
        settings.run.docker_screen = docker_screen

    log.debug("Settings override:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Backend: {str(settings.run.backend)}\n"
              f"- Entrypoint: {str(settings.run.entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Docker screen: {str(settings.run.docker_screen)}\n"
              f"- NDS ROM: {str(nds)}\n"
              )
    run_command(
        nds=nds, image=image,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )

@app.command("build")
def build_controller(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False
):
    """devkitARM make wrapper. Builds NDS ROM from source code."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              )

    # CLI overrides
    if backend is not None:
        settings.build.backend = backend
    if entrypoint is not None:
        settings.build.entrypoint = entrypoint

    log.debug("Final settings for build command:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Backend: {str(settings.build.backend)}\n"
              f"- Entrypoint: {str(settings.build.entrypoint)}\n"
              )

    build_command(
        d=directory,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )



@app.command("patch")
def patch_controller(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False,
):
    """dlditool wrapper. Patches a NDS ROM for FAT usage."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              )

    # CLI overrides
    if backend is not None:
        settings.patch.backend = backend
    if entrypoint is not None:
        settings.patch.entrypoint = entrypoint

    log.debug("Final settings for build command:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(settings.patch.backend)}\n"
              f"- Entrypoint: {str(settings.patch.entrypoint)}\n"
              )

    patch_command(
        d=directory,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )



@app.command("git")
def git_controller(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
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
        vpn_test_ip: VpnTestIpOpt = None
):
    """git wrapper with SSH password bypass and VPN management. git is a distributed version control system."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"

              f"- SSH username: {str(ssh_username)}\n"
              f"- SSH password: {str(ssh_password)}\n"
              f"- SSH host: {str(ssh_host)}\n"
              f"- git name: {str(git_name)}\n"
              f"- git email: {str(git_email)}\n"
              f"- VPN username: {str(vpn_username)}\n"
              f"- VPN password: {str(vpn_password)}\n"
              f"- VPN host: {str(vpn_host)}\n"
              f"- VPN port: {str(vpn_port)}\n"
              f"- VPN realm: {str(vpn_realm)}\n"
              f"- VPN cert: {str(vpn_cert)}\n"
              f"- VPN test DNS: {str(vpn_test_dns)}\n"
              f"- VPN test IP: {str(vpn_test_ip)}\n"
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

    log.debug("Final settings for git command:\n"
              f"- Arguments: {str(arguments)}\n"
              
              f"- Directory: {str(directory)}\n"
              f"- Shell: {str(shell)}\n"
              f"- Dry run: {str(dry_run)}\n"
              
              f"- Backend: {str(settings.git.backend)}\n"
              f"- Entrypoint: {str(settings.git.entrypoint)}\n"

              f"- SSH username: {str(settings.git.ssh.username)}\n"
              f"- SSH password: {str(settings.git.ssh.password)}\n"
              f"- SSH server: {str(settings.git.ssh.host)}\n"
              f"- git name: {str(settings.git.git.name)}\n"
              f"- git email: {str(settings.git.git.email)}\n"
              f"- VPN username: {str(settings.git.vpn.username)}\n"
              f"- VPN password: {str(settings.git.vpn.password)}\n"
              f"- VPN host: {str(settings.git.vpn.host)}\n"
              f"- VPN port: {str(settings.git.vpn.port)}\n"
              f"- VPN realm: {str(settings.git.vpn.realm)}\n"
              f"- VPN cert: {str(settings.git.vpn.cert)}\n"
              f"- VPN test DNS: {str(settings.git.vpn.test_dns)}\n"
              f"- VPN test IP: {str(settings.git.vpn.test_ip)}\n"
              )

    git_command(
        d=directory,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )



