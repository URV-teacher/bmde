"""
Reusable CLI argument definition.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from bmde.config.show_config import show_config_callback, show_default_config_callback
from bmde.core.types import BackendOptions, DockerOutputOptions

# Backend option for the rest of commands other than run
BackendOpt = Annotated[
    BackendOptions | None,
    typer.Option(
        "-b",
        "--backend",
        help="Backend to execute command:" " host|docker|flatpak",
        case_sensitive=False,
    ),
]

# Arguments passed directly to the entrypoint
ArgumentsOpt = Annotated[
    list[str] | None,
    typer.Argument(help="Arguments that are passed to the backend entrypoint."),
]

# Argument to send a directory
DirectoryOpt = Annotated[
    Path | None,
    typer.Option(
        "-d",
        "--directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to a directory. If omitted, the current directory is used.",
    ),
]


# Path to file that will be used as entrypoint
EntrypointOpt = Annotated[
    Path | None,
    typer.Option("--entrypoint", help="Override backend entrypoint executable"),
]

### Global options
# Dry-run flag
DryRunOpt = Annotated[
    bool,
    typer.Option("--dry-run", help="Simulate actions without executing", is_flag=True),
]

InteractiveOpt = Annotated[
    bool,
    typer.Option(
        "--interactive",
        help="Run in interactive mode (allocates TTY)",
    ),
]

LogFileOpt = Annotated[
    Path | None, typer.Option("-l", "--log-file", help="Path to log file (optional)")
]

ShowConfigOpt = Annotated[
    bool,
    typer.Option(
        "-s",
        "--show-config",
        callback=show_config_callback,
        is_eager=True,
        help="Show current configuration options. Can be used to freeze BMDE arguments into a bmde.toml configuration "
        "file",
        is_flag=True,
    ),
]

ShowDefaultConfigOpt = Annotated[
    bool,
    typer.Option(
        "-d",
        "--show-default-config",
        callback=show_default_config_callback,
        is_eager=True,
        help="Show default configuration options. Can be used as template of a bmde.toml configuration file",
        is_flag=True,
    ),
]

VerboseOpt = Annotated[
    bool,
    typer.Option(
        "-v", "--verbose", "--debug", help="Verbose output (debug)", is_flag=True
    ),
]

# Very verbose flag
VeryVerboseOpt = Annotated[
    bool,
    typer.Option("--t", "--trace", help="Very verbose output (trace)", is_flag=True),
]

# Quiet flag
QuietOpt = Annotated[
    bool,
    typer.Option("-q", "--quiet", help="Quiet mode (minimal output)", is_flag=True),
]

# Very quiet flag
VeryQuietOpt = Annotated[
    bool,
    typer.Option(
        "-Q", "--Quiet", "--no-output", help="Quiet mode (no output)", is_flag=True
    ),
]

ConfigOpt = Annotated[
    Path | None,
    typer.Option(
        "-c", "--config", help="Execution-specific config file (highest file priority)"
    ),
]

# --- Run options ---
# To specify debug in run options
DebugOpt = Annotated[
    bool, typer.Option("--debug", help="Enable GDB stub if supported", is_flag=True)
]

# To specify the debug port in options
PortOpt = Annotated[
    int, typer.Option("-p", "--port", help="Debug port (implies --debug)")
]

DockerNetworkOpt = Annotated[
    str | None,
    typer.Option(
        "-N",
        "--docker-network",
        "--network",
        help='Name of the Docker network to use when using the "docker" environment',
        is_flag=True,
    ),
]


DockerScreenOpt = Annotated[
    DockerOutputOptions | None,
    typer.Option(
        "-s",
        "--screen",
        help='Method to show the screen when using the "docker" environment',
        is_flag=True,
    ),
]


BackgroundOpt = Annotated[
    bool,
    typer.Option("-B", "--background", help="Run background", is_flag=True),
]

NdsRomOpt = Annotated[
    Path | None,
    typer.Option(
        "-n",
        "--nds",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the .nds binary (optional). If omitted, searches the current directory.",
    ),
]


ElfRomOpt = Annotated[
    Path | None,
    typer.Option(
        "-e",
        "--elf",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the .elf binary. If omitted, searches the current directory for an elf.",
    ),
]

FatImageOpt = Annotated[
    Path | None,
    typer.Option(
        "-i",
        "--image",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to FAT image (optional)",
    ),
]

# Git


SshUsernameOpt = Annotated[
    str | None,
    typer.Option("--ssh-user", help="User name for the SSH authentication of git"),
]

SshPasswordOpt = Annotated[
    str | None,
    typer.Option(
        "--ssh-password", help="User password for the SSH authentication of git"
    ),
]

SshHostOpt = Annotated[
    str | None, typer.Option("--ssh-server", help="Hostname of the ssh server")
]

GitNameOpt = Annotated[
    str | None,
    typer.Option("--git-password", help="User name for git commit signature"),
]

GitEmailOpt = Annotated[
    str | None,
    typer.Option("--git-email", help="User email for git commit signature"),
]

VpnUsernameOpt = Annotated[
    str | None,
    typer.Option("--vpn-user", help="User name for forticlient authentication"),
]

VpnPasswordOpt = Annotated[
    str | None,
    typer.Option("--vpn-password", help="User password for forticlient authentication"),
]

VpnHostOpt = Annotated[
    str | None, typer.Option("--vpn-gateway", help="VPN gateway for forticlient")
]

VpnPortOpt = Annotated[
    int | None, typer.Option("--vpn-port", help="VPN port for forticlient")
]

VpnRealmOpt = Annotated[
    str | None, typer.Option("--vpn-realm", help="VPN realm for forticlient")
]

VpnCertOpt = Annotated[
    str | None, typer.Option("--vpn-cert", help="VPN cert for forticlient")
]

VpnTestDnsOpt = Annotated[
    str | None,
    typer.Option(
        "--vpn-test-dns",
        help="DNS direction that will be tested with an HTTP GET request to validate that we can access the "
        "internal "
        "services granted by the VPN and its implicit DNS resolution",
    ),
]

VpnTestIpOpt = Annotated[
    str | None,
    typer.Option(
        "--vpn-test-ip",
        help="IP direction that will be tested with an HTTP GET request to validate that we can access the internal "
        "services granted by the VPN",
    ),
]


# TODO Add all opts to this variable so they are marked as publicly exposed
__all__ = [
    "EntrypointOpt",
    "DebugOpt",
    "PortOpt",
    "DryRunOpt",
    "VerboseOpt",
    "QuietOpt",
    "DockerScreenOpt",
    "ConfigOpt",
    "BackendOpt",
    "ArgumentsOpt",
    "DirectoryOpt",
    "VeryVerboseOpt",
    "VeryQuietOpt",
    "LogFileOpt",
    "NdsRomOpt",
    "FatImageOpt",
    "SshUsernameOpt",
    "SshPasswordOpt",
    "SshHostOpt",
    "GitNameOpt",
    "GitEmailOpt",
    "VpnUsernameOpt",
    "VpnPasswordOpt",
    "VpnHostOpt",
    "VpnPortOpt",
    "VpnRealmOpt",
    "VpnCertOpt",
    "VpnTestDnsOpt",
    "VpnTestIpOpt",
    "ConfigOpt",
    "ElfRomOpt",
    "DockerNetworkOpt",
    "BackgroundOpt",
    "ShowConfigOpt",
    "InteractiveOpt",
    "ShowDefaultConfigOpt",
]
