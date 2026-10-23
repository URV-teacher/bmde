# bmde - Bare Metal Development Environment CLI
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Reusable CLI argument definition."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from bmde.config.show_config import show_config_callback, show_default_config_callback
from bmde.core.types import BackendOptions, DebuggerOptions, DockerOutputOptions

# Backend option for the rest of commands other than run
BackendOpt = Annotated[
    BackendOptions | None,
    typer.Option(
        "-b",
        "--backend",
        help="Backend to execute command: host|docker|flatpak",
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
    typer.Option("--dry-run", help="Simulate actions without executing"),
]

InteractiveOpt = Annotated[
    bool,
    # Without --no-interactive the flag could not be turned off, which scripts and CI (without a TTY) need
    typer.Option(
        "--interactive/--no-interactive",
        help="Run in interactive mode (allocates TTY)",
    ),
]

LogFileOpt = Annotated[Path | None, typer.Option("-l", "--log-file", help="Path to log file (optional)")]

ShowConfigOpt = Annotated[
    bool,
    typer.Option(
        "-s",
        "--show-config",
        callback=show_config_callback,
        is_eager=True,
        help="Show current configuration options. Can be used to freeze BMDE arguments into a bmde.toml configuration "
        "file",
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
    ),
]


def version_callback(value: bool) -> None:
    if value:
        # The version of the installed distribution, which hatch-vcs takes from the git tag (also for editable installs)
        typer.echo(f"bmde {version('bmde')}")
        raise typer.Exit()


VersionOpt = Annotated[
    bool,
    typer.Option(
        "-V",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version of bmde and exit",
    ),
]

VerboseOpt = Annotated[
    bool,
    typer.Option("-v", "--verbose", "--debug", help="Verbose output (debug)"),
]

# Very verbose flag
VeryVerboseOpt = Annotated[
    bool,
    typer.Option("--t", "--trace", help="Very verbose output (trace)"),
]

# Quiet flag
QuietOpt = Annotated[
    bool,
    typer.Option("-q", "--quiet", help="Quiet mode (minimal output)"),
]

# Very quiet flag
VeryQuietOpt = Annotated[
    bool,
    typer.Option("-Q", "--Quiet", "--no-output", help="Quiet mode (no output)"),
]

ConfigOpt = Annotated[
    Path | None,
    typer.Option(
        "-c",
        "--config",
        help="Execution-specific config file (beats the other files and the BMDE_* environment variables)",
    ),
]

# --- Run options ---
# To specify debug in run options
# None when not given, so the debug option of the settings applies
DebugOpt = Annotated[bool | None, typer.Option("--debug", help="Enable GDB stub if supported")]

# To specify the debug port in options
PortOpt = Annotated[int | None, typer.Option("-p", "--port", help="Debug port (implies --debug)")]

DebuggerOpt = Annotated[
    DebuggerOptions | None,
    typer.Option("-g", "--debugger", help="Debugger connected to the emulator"),
]

DockerNetworkOpt = Annotated[
    str | None,
    typer.Option(
        "-N",
        "--docker-network",
        "--network",
        help='Name of the Docker network to use when using the "docker" environment',
    ),
]


DockerScreenOpt = Annotated[
    DockerOutputOptions | None,
    typer.Option(
        "-s",
        "--screen",
        help='Method to show the screen when using the "docker" environment',
    ),
]


BackgroundOpt = Annotated[
    bool,
    typer.Option("-B", "--background", help="Run background"),
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

SoundOpt = Annotated[
    bool | None,
    typer.Option(
        "--sound/--no-sound",
        help="Play the emulator sound on the host (docker: shares the host PulseAudio/PipeWire socket)",
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

ControlsOpt = Annotated[
    Path | None,
    typer.Option(
        "--controls",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a DeSmuME desmume.ini with custom controls (and HUD options) (optional)",
    ),
]

# Git


SshUsernameOpt = Annotated[
    str | None,
    typer.Option("--ssh-user", help="User name for the SSH authentication of git"),
]

SshPasswordOpt = Annotated[
    str | None,
    typer.Option("--ssh-password", help="User password for the SSH authentication of git"),
]

SshHostOpt = Annotated[str | None, typer.Option("--ssh-server", help="Hostname of the ssh server")]

GitNameOpt = Annotated[
    str | None,
    # --git-password is the name previous versions gave to this option by mistake
    typer.Option("--git-name", "--git-password", help="User name for git commit signature"),
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

VpnHostOpt = Annotated[str | None, typer.Option("--vpn-gateway", help="VPN gateway for forticlient")]

VpnPortOpt = Annotated[int | None, typer.Option("--vpn-port", help="VPN port for forticlient")]

VpnRealmOpt = Annotated[str | None, typer.Option("--vpn-realm", help="VPN realm for forticlient")]

VpnCertOpt = Annotated[str | None, typer.Option("--vpn-cert", help="VPN cert for forticlient")]

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

# None when not given, so the git.vpn.enabled option of the settings applies
VpnOpt = Annotated[
    bool | None,
    typer.Option("--vpn/--no-vpn", help="Run git through the VPN of the URV (not needed inside its network)"),
]


# TODO Add all opts to this variable so they are marked as publicly exposed
__all__ = [
    "ArgumentsOpt",
    "BackendOpt",
    "BackgroundOpt",
    "ConfigOpt",
    "ControlsOpt",
    "DebugOpt",
    "DebuggerOpt",
    "DirectoryOpt",
    "DockerNetworkOpt",
    "DockerScreenOpt",
    "DryRunOpt",
    "ElfRomOpt",
    "EntrypointOpt",
    "FatImageOpt",
    "GitEmailOpt",
    "GitNameOpt",
    "InteractiveOpt",
    "LogFileOpt",
    "NdsRomOpt",
    "PortOpt",
    "QuietOpt",
    "ShowConfigOpt",
    "ShowDefaultConfigOpt",
    "SoundOpt",
    "SshHostOpt",
    "SshPasswordOpt",
    "SshUsernameOpt",
    "VerboseOpt",
    "VeryQuietOpt",
    "VeryVerboseOpt",
    "VpnCertOpt",
    "VpnHostOpt",
    "VpnOpt",
    "VpnPasswordOpt",
    "VpnPortOpt",
    "VpnRealmOpt",
    "VpnTestDnsOpt",
    "VpnTestIpOpt",
    "VpnUsernameOpt",
]
