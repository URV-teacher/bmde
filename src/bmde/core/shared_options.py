"""
Reusable CLI argument definition.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Annotated

import typer

from bmde.core.types import BackendOptions, RunBackendOptions, DockerOutputOptions

# Backend options for run command
RunBackendOpt = Annotated[
    Optional[RunBackendOptions],
    typer.Option(
        "-b",
        "--backend",
        help="Backend to execute command:" " host|docker|flatpak",
        case_sensitive=False,
    ),
]

# Backend option for the rest of commands other than run
BackendOpt = Annotated[
    Optional[BackendOptions],
    typer.Option(
        "-b",
        "--backend",
        help="Backend to execute command:" " host|docker",
        case_sensitive=False,
    ),
]

# Arguments passed directly to the entrypoint
ArgumentsOpt = Annotated[
    Optional[list[str]],
    typer.Argument(help="Arguments that are passed to the backend entrypoint."),
]

# Argument to send a directory
DirectoryOpt = Annotated[
    Optional[Path],
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
    Optional[Path],
    typer.Option("--entrypoint", help="Override backend entrypoint executable"),
]

### Global options
# Dry-run flag
DryRunOpt = Annotated[
    bool,
    typer.Option("--dry-run", help="Simulate actions without executing", is_flag=True),
]

LogFileOpt = Annotated[
    Optional[Path], typer.Option("-l", "--log-file", help="Path to log file (optional)")
]

# Verbose flag
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
    Optional[Path],
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
    Optional[DockerOutputOptions],
    typer.Option(
        "-n",
        "--docker-network",
        "--network",
        help='Name of the Docker network to use when using the "docker" environment',
        is_flag=True,
    ),
]


DockerScreenOpt = Annotated[
    Optional[DockerOutputOptions],
    typer.Option(
        "-s",
        "--screen",
        help='Method to show the screen when using the "docker" environment',
        is_flag=True,
    ),
]


BackgroundOpt = Annotated[
    bool,
    typer.Option("-b", "--background", help="Run background", is_flag=True),
]

NdsRomOpt = Annotated[
    Optional[Path],
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
    Optional[Path],
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
    Optional[Path],
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
    Optional[str],
    typer.Option("--ssh-user", help="User name for the SSH authentication of git"),
]

SshPasswordOpt = Annotated[
    Optional[str],
    typer.Option(
        "--ssh-password", help="User password for the SSH authentication of git"
    ),
]

SshHostOpt = Annotated[
    Optional[str], typer.Option("--ssh-server", help="Hostname of the ssh server")
]

GitNameOpt = Annotated[
    Optional[str],
    typer.Option("--git-password", help="User name for git commit signature"),
]

GitEmailOpt = Annotated[
    Optional[str],
    typer.Option("--git-email", help="User email for git commit signature"),
]

VpnUsernameOpt = Annotated[
    Optional[str],
    typer.Option("--vpn-user", help="User name for forticlient authentication"),
]

VpnPasswordOpt = Annotated[
    Optional[str],
    typer.Option("--vpn-password", help="User password for forticlient authentication"),
]

VpnHostOpt = Annotated[
    Optional[str], typer.Option("--vpn-gateway", help="VPN gateway for forticlient")
]

VpnPortOpt = Annotated[
    Optional[str], typer.Option("--vpn-port", help="VPN port for forticlient")
]

VpnRealmOpt = Annotated[
    Optional[str], typer.Option("--vpn-realm", help="VPN realm for forticlient")
]

VpnCertOpt = Annotated[
    Optional[str], typer.Option("--vpn-cert", help="VPN cert for forticlient")
]

VpnTestDnsOpt = Annotated[
    Optional[str],
    typer.Option(
        "--vpn-test-dns",
        help="DNS direction that will be tested with an HTTP GET request to validate that we can access the "
        "internal "
        "services granted by the VPN and its implicit DNS resolution",
    ),
]

VpnTestIpOpt = Annotated[
    Optional[str],
    typer.Option(
        "--vpn-test-ip",
        help="IP direction that will be tested with an HTTP GET request to validate that we can access the internal "
        "services granted by the VPN",
    ),
]


# TODO Add all opts to this variable so they are marked as publicly exposed
__all__ = [
    "RunBackendOpt",
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
]
