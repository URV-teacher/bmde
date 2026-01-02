from __future__ import annotations

import os
from pathlib import Path
from subprocess import Popen
from typing import Optional

from bmde.core import logging
from bmde.core.exec import ExecOptions
from .service import GitService
from .settings import GitSettings
from .spec import GitSpec, GitSpecOpts
from ...config.loader import load_settings
from ...core.logging import setup_logging, LogLevel
from ...core.spec_opts import SpecExecOpts
from ...core.types import BackendOptions

log = logging.get_logger(__name__)


def create_git_spec(
    d: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    interactive: bool = True,
    dry_run: bool = True,
    entrypoint: Optional[Path] = None,
    ssh_username: Optional[str] = None,
    ssh_password: Optional[str] = None,
    ssh_host: Optional[str] = None,
    git_name: Optional[str] = None,
    git_email: Optional[str] = None,
    vpn_username: Optional[str] = None,
    vpn_password: Optional[str] = None,
    vpn_host: Optional[str] = None,
    vpn_port: Optional[int] = None,
    vpn_realm: Optional[str] = None,
    vpn_cert: Optional[str] = None,
    vpn_test_dns: Optional[str] = None,
    vpn_test_ip: Optional[str] = None,
    settings: Optional[GitSettings] = None,
) -> GitSpec:
    if d is None:
        d = Path(os.getcwd())

    if settings is None:
        settings = GitSettings()

    return GitSpec(
        GitSpecOpts=GitSpecOpts(
            d=d,
            ssh_username=(
                ssh_username if ssh_username is not None else settings.ssh.username
            ),
            ssh_password=(
                ssh_password if ssh_password is not None else settings.ssh.password
            ),
            ssh_host=ssh_host if ssh_host is not None else settings.ssh.host,
            git_name=git_name if git_name is not None else settings.git.name,
            git_email=git_email if git_email is not None else settings.git.email,
            vpn_username=(
                vpn_username if vpn_username is not None else settings.vpn.username
            ),
            vpn_password=(
                vpn_password if vpn_password is not None else settings.vpn.password
            ),
            vpn_host=vpn_host if vpn_host is not None else settings.vpn.host,
            vpn_port=vpn_port if vpn_port is not None else settings.vpn.port,
            vpn_realm=vpn_realm if vpn_realm is not None else settings.vpn.realm,
            vpn_cert=vpn_cert if vpn_cert is not None else settings.vpn.cert,
            vpn_test_dns=(
                vpn_test_dns if vpn_test_dns is not None else settings.vpn.test_dns
            ),
            vpn_test_ip=(
                vpn_test_ip if vpn_test_ip is not None else settings.vpn.test_ip
            ),
        ),
        SpecExecOpts=SpecExecOpts(
            backend=(
                backend
                if backend is not None
                else (
                    settings.execution_settings.backend
                    if settings.execution_settings.backend is not None
                    else BackendOptions.DOCKER
                )
            ),
            entrypoint=(
                entrypoint
                if entrypoint is not None
                else settings.execution_settings.entrypoint
            ),
            arguments=arguments,
            dry_run=(
                dry_run if dry_run is not None else settings.execution_settings.dry_run
            ),
            background=(
                settings.execution_settings.background
                if settings.execution_settings.background is not None
                else False
            ),
            interactive=(
                interactive
                if interactive is not None
                else settings.execution_settings.interactive
            ),
        ),
    )


def execute_git(spec: GitSpec) -> int | Popen[bytes]:
    return GitService().run(
        spec.GitSpecOpts,
        ExecOptions(
            dry_run=spec.SpecExecOpts.dry_run,
            background=spec.SpecExecOpts.background,
            interactive=spec.SpecExecOpts.interactive,
            entrypoint=spec.SpecExecOpts.entrypoint,
            arguments=spec.SpecExecOpts.arguments,
            backend=spec.SpecExecOpts.backend,
        ),
    )


def git_command(
    d: Optional[Path],
    arguments: Optional[list[str]] = None,
    backend: Optional[BackendOptions] = None,
    dry_run: bool = False,
    interactive: bool = True,
    entrypoint: Optional[Path] = None,
    ssh_username: Optional[str] = None,
    ssh_password: Optional[str] = None,
    ssh_host: Optional[str] = None,
    git_name: Optional[str] = None,
    git_email: Optional[str] = None,
    vpn_username: Optional[str] = None,
    vpn_password: Optional[str] = None,
    vpn_host: Optional[str] = None,
    vpn_port: Optional[int] = None,
    vpn_realm: Optional[str] = None,
    vpn_cert: Optional[str] = None,
    vpn_test_dns: Optional[str] = None,
    vpn_test_ip: Optional[str] = None,
    settings: Optional[GitSettings] = None,
) -> int | Popen[bytes]:

    if settings is None:
        settings = load_settings()
        setup_logging(
            LogLevel(settings.logging.level).to_logging_level(),
            log_file=settings.logging.file,
        )
        settings = settings.git

    spec = create_git_spec(
        d=d,
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
        settings=settings,
    )

    return execute_git(spec)
