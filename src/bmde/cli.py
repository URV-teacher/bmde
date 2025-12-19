"""
The responsibility of this file is to implement the functions that will be called when calling each subcommand in the
CLI. Each function is responsible for attending a single subcommand with their arguments specified through the function
typehint arguments using Typer. Each function will build a Settings object with the CLI overrides, arguments and default
settings, which will be passed to the function and run a command.
Each function will also be responsible for aborting execution with CLI arguments that are impossible. This only applies
to data coming from the CLI, the syntax of the overrides is not responsibility of the function of these files.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Annotated, LiteralString

import typer
from pygments.lexers import shell
from rich.console import Console

from .config.loader import load_settings
from .config.schema import Settings
from .core import logging
from .core.logging import setup_logging
from .core.types import PROJECT_DIR, LogLevel, NOW
from .git.command import git_nds_command
from .shared_options import (
    RunBackendOpt, EntrypointOpt, DebugOpt, PortOpt,
    DryRunOpt, VerboseOpt, QuietOpt, DockerScreenOpt, BackendOpt, ArgumentsOpt, DirectoryOpt, ShellOpt,
    VeryVerboseOpt, VeryQuietOpt, LogFileOpt, InfoOpt,
)

console = Console()
app = typer.Typer(add_completion=False, help="bmde – BMDE CLI", no_args_is_help=True)  # TODO Completion does not work
log = logging.get_logger(__name__)

def get_default_log_path() -> LiteralString | str | bytes:
    return os.path.join(PROJECT_DIR, "logs", NOW + ".log")

@app.callback()
def _global(ctx: typer.Context,
            config: Optional[Path] = typer.Option(None, "-c", "--config",
                help="Execution-specific config file (highest file priority)"),
            verbose: VerboseOpt = False,
            very_verbose: VeryVerboseOpt = False,
            info: InfoOpt = False,
            quiet: QuietOpt = False,
            very_quiet: VeryQuietOpt = False,
            log_file: LogFileOpt = None,
            ):
    """
    Global option callback. Executed if no command is provided.
    """
    # Preventive creation of logger if CLI options are provided before loading settings
    log_level = None
    if very_verbose is True:
        log_level = LogLevel.TRACE
    elif verbose is True:
        log_level = LogLevel.DEBUG
    elif quiet is True:
        log_level = LogLevel.WARNING
    elif very_quiet is True:
        log_level = LogLevel.QUIET
    elif info is True:
        log_level = LogLevel.INFO

    preventive_log_level = None
    if log_level is not None:
        preventive_log_level = log_level.to_logging_level()
    else:
        preventive_log_level = LogLevel.INFO.to_logging_level()  # Default if no CLI option specified

    if log_file is None:
        preventive_log_file = get_default_log_path()
    else:
        preventive_log_file = log_file

    setup_logging(preventive_log_level, log_file=preventive_log_file)  # Preventive creation of log for logging the loading of settings

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
def run_command(
    ctx: typer.Context,

    nds: Optional[Path] = typer.Option(
        None, "-n", "--nds",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True,
        help="Path to the .nds binary (optional). If omitted, bmde searches the current directory.",
    ),
    image: Optional[Path] = typer.Option(
        None, "-i", "--image",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True,
        help="Path to FAT image (optional)",
    ),
    shell: ShellOpt = False,
    arguments: ArgumentsOpt = (),
    docker_screen: Optional[DockerScreenOpt] = typer.Option(None, "--docker-screen", help="Selects the method to show the desmume "
                                                                   "screen. "
                                                                   "Can be vnc or host",
                                                      show_default=False),
    # common flags
    backend: RunBackendOpt = None,
    entrypoint: EntrypointOpt = None,
    debug: DebugOpt = False,
    port: PortOpt = 1000,
    dry_run: DryRunOpt = False,
):

    """desmume wrapper. Runs an NDS ROM."""
    from .run.command import run_nds_command

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Shell: {str(shell)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Docker screen: {str(docker_screen)}\n"
              f"- NDS ROM: {str(nds)}\n"
              )

    # CLI logic
    if entrypoint is not None and shell is True:
        log.warning("The --entrypoint option is incompatible with --shell, entrypoint will be ignored")

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
              f"- Shell: {str(shell)}\n"
              f"- Backend: {str(settings.run.backend)}\n"
              f"- Entrypoint: {str(settings.run.entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Docker screen: {str(settings.run.docker_screen)}\n"
              f"- NDS ROM: {str(nds)}\n"
              )
    run_nds_command(
        nds=nds, image=image, shell=shell,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )



@app.command("build")
def build_command(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False
):


    """devkitARM make wrapper. Builds NDS ROM from source code."""
    from .build.command import build_nds_command

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

    build_nds_command(
        d=directory,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )



@app.command("patch")
def patch_command(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        directory: DirectoryOpt = os.getcwd(),
        shell: ShellOpt = False,
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False,
):

    """dlditool wrapper. Patches a NDS ROM for FAT usage."""
    from .patch.command import patch_nds_command

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Shell: {str(shell)}\n"
              f"- Backend: {str(backend)}\n"
              f"- Entrypoint: {str(entrypoint)}\n"
              f"- Dry run: {str(dry_run)}\n"
              )

    # CLI logic
    if entrypoint is not None and shell is True:
        log.warning("The --entrypoint option is incompatible with --shell, entrypoint will be ignored")

    # CLI overrides
    if backend is not None:
        settings.patch.backend = backend
    if entrypoint is not None:
        settings.patch.entrypoint = entrypoint

    log.debug("Final settings for build command:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Shell: {str(shell)}\n"
              f"- Dry run: {str(dry_run)}\n"
              f"- Backend: {str(settings.patch.backend)}\n"
              f"- Entrypoint: {str(settings.patch.entrypoint)}\n"
              )

    patch_nds_command(
        d=directory, shell=shell,
        arguments=arguments or [], settings=settings, dry_run=dry_run
    )



@app.command("git")
def git_command(
        ctx: typer.Context,
        arguments: ArgumentsOpt = (),
        clone: Annotated[str, typer.Option(
            "--clone",
            help="Repos to clone, specified as REPO_NAME1@SHAID1,REPO_NAME2@SHAID2,REPO_NAME3@SHAID3... The SHAIDX are"
                 " optional. If present ignores arguments.",
        )] = None, # TODO
        json_file: Annotated[Path, typer.Option(
            "--json",
            help="Deliveries to clone and checkout, in JSON delivery format. If present ignores arguments.",
        )] = None,
        directory: DirectoryOpt = os.getcwd(),
        shell: ShellOpt = False,
        backend: BackendOpt = None,
        entrypoint: EntrypointOpt = None,
        dry_run: DryRunOpt = False,

        ssh_username: Annotated[str, typer.Option(
            "--ssh-user",
            help="User name for the SSH authentication of git",
        )] = None,

        ssh_password: Annotated[str, typer.Option(
            "--ssh-password",
            help="User password for the SSH authentication of git",
        )] = None,

        ssh_host: Annotated[str, typer.Option(
            "--ssh-server",
            help="Hostname of the ssh server",
        )] = None,

        git_name: Annotated[str, typer.Option(
            "--git-password",
            help="User name for git commit signature",
        )] = None,

        git_email: Annotated[str, typer.Option(
            "--git-email",
            help="User email for git commit signature",
        )] = None,

        vpn_username: Annotated[str, typer.Option(
            "--vpn-user",
            help="User name for forticlient authentication",
        )] = None,

        vpn_password: Annotated[str, typer.Option(
            "--vpn-password",
            help="User password for forticlient authentication",
        )] = None,

        vpn_host: Annotated[str, typer.Option(
            "--vpn-gateway",
            help="VPN gateway for forticlient",
        )] = None,

        vpn_port: Annotated[str, typer.Option(
            "--vpn-port",
            help="VPN port for forticlient",
        )] = None,

        vpn_realm: Annotated[str, typer.Option(
            "--vpn-realm",
            help="VPN realm for forticlient",
        )] = None,

        vpn_cert: Annotated[str, typer.Option(
            "--vpn-cert",
            help="VPN cert for forticlient",
        )] = None,

        vpn_test_dns: Annotated[str, typer.Option(
            "--vpn-test-dns",
            help="DNS direction that will be tested with an HTTP GET request to validate that we can access the "
                 "internal "
                 "services granted by the VPN and its implicit DNS resolution",
        )] = None,

        vpn_test_ip: Annotated[str, typer.Option(
            "--vpn-test-ip",
            help="IP direction that will be tested with an HTTP GET request to validate that we can access the internal "
                 "services granted by the VPN",
        )] = None
):


    """git wrapper with SSH password bypass and VPN management. git is a distributed version control system."""

    settings: Settings = ctx.obj["settings"]

    log.debug("CLI options provided:\n"
              f"- Arguments: {str(arguments)}\n"
              f"- Clone: {str(clone)}\n"
              f"- Directory: {str(directory)}\n"
              f"- Json: {str(json_file)}\n"
              f"- Shell: {str(shell)}\n"
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

    # CLI logic
    if entrypoint is not None and shell is True:
        log.warning("The --entrypoint option is incompatible with --shell, entrypoint will be ignored")
    if arguments is not None and clone is not None:
        log.warning("The --arguments option is incompatible with --clone, arguments will be ignored")

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

    if clone is None and json_file is None:
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

        git_nds_command(
            d=directory, shell=shell,
            arguments=arguments or [], settings=settings, dry_run=dry_run
        )
    else:

        clone_tasks = []

        if clone is not None:
            for repo_shaid in clone.split(","):
                if "@" in repo_shaid:
                    name = repo_shaid.split("@")[0]
                    shaid = repo_shaid.split("@")[1]
                else:
                    name = repo_shaid
                    shaid = None
                clone_tasks.append((name, shaid, name))
        if json_file is not None:
            import json
            obj = json.loads("".join(open(json_file).readlines()))
            base_name = f"{obj['repo']}-{obj['role']}-phase{obj['phase']}-call{obj['call']}"
            clone_tasks.append((obj["repo"], obj["test"], base_name + "-test"))
            clone_tasks.append((obj["repo"], obj["fusion"], base_name + "-fusion"))

        log.debug("Final settings for git command in clone mode:\n"
                  f"- Clone tasks: {str(clone_tasks)}\n"

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

        for clone_task in clone_tasks:
            log.debug(f"Executing clone task for cloning repo {clone_task[0]}")
            git_nds_command(
                d=directory, shell=shell,
                arguments=["clone", settings.git.ssh.username + "@" + settings.git.ssh.host + ":" + clone_task[0]], settings=settings, dry_run=dry_run
            )
            if clone_task[0] != clone_task[2]:  # Name has been specified different from repo name, rename
                log.debug(f"Renaming {clone_task[0]} into {clone_task[2]}")
                os.rename(clone_task[0], clone_task[2])
                repo_directory = os.path.join(directory, clone_task[2])
            else:
                repo_directory = os.path.join(directory, clone_tasks[1])


            if clone_tasks[1] is not None:
                log.debug(f"Checking out SHA ID {clone_task[1]} from repo {clone_task[0]} in folder {repo_directory}")
                git_nds_command(
                    d=repo_directory, shell=shell,
                    arguments=["checkout", clone_task[1]], settings=settings, dry_run=dry_run
                )



