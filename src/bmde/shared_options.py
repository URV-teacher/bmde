"""
Reusable CLI argument definition.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, List
from typing_extensions import Annotated
import typer

from bmde.core.types import Backend, RunBackend, RunDockerOutputName

# Backend options for run command
RunBackendOpt = Annotated[
    Optional[RunBackend],
    typer.Option(
        "-b",
        "--backend",
        help="Backend to execute command:"
             " host|docker|flatpak",
        case_sensitive=False,
    ),
]

# Backend option for the rest of commands other than run
BackendOpt = Annotated[
    Optional[Backend],
    typer.Option(
        "-b",
        "--backend",
        help="Backend to execute command:"
             " host|docker",
        case_sensitive=False,
    ),
]

# Arguments passed directly to the entrypoint
ArgumentsOpt = Annotated[
    List[str],
    typer.Argument(help="Arguments are passed directly to the backend entrypoint.")]

# Argument to send a directory
DirectoryOpt = Annotated[
    Path,
    typer.Option("-d", "--directory",
                                                exists=True,
                                                file_okay=False,
                                                dir_okay=True,
                                                readable=True,
                                                resolve_path=True,
                                                help="Path to a directory. If omitted, the current directory is used.")]

# Argument to send a target
DirectoryTargetOpt = Annotated[
    Path,
    typer.Option("-t", "--target",
                                                exists=True,
                                                file_okay=False,
                                                dir_okay=True,
                                                readable=True,
                                                resolve_path=True,
                                                help="Path to the target directory where the test project will be "
                                                     "prepared. If omitted, the current directory plus the folder test "
                                                     "($CWD/test) is used.")]

# Argument to send a target
DirectoryTestOpt = Annotated[
    Path,
    typer.Option("-j", "--test", "--jprofes",
                                                exists=True,
                                                file_okay=False,
                                                dir_okay=True,
                                                readable=True,
                                                resolve_path=True,
                                                help="Path to the directory where the test project is. It will be copied "
                                                     "into the target directory.")]

# Argument to request a shell, only usable in docker backends
ShellOpt = Annotated[bool, typer.Option("-s", "--shell",
                                            is_flag=True,
                                            help="Open backend shell (docker only)")]

# Path to file that will be used as entrypoint
EntrypointOpt = Annotated[
    Optional[Path],
    typer.Option(
        "--entrypoint",
        help="Override backend entrypoint executable",
    ),
]

# Dry-run flag
DryRunOpt = Annotated[
    bool,
    typer.Option(
        "--dry-run",
        help="Simulate actions without executing",
        is_flag=True,
    ),
]

LogFileOpt = Annotated[
    Path,
    typer.Option(
        "-l",
        "--log-file",
        help="Path to log file (optional)"),
]

# Quiet flag
InfoOpt = Annotated[
    bool,
    typer.Option(
        "-i",
        "--info",
        help="Info mode (default output)",
        is_flag=True,
    ),
]

# Verbose flag
VerboseOpt = Annotated[
    bool,
    typer.Option(
        "-v",
        "--verbose",
        "--debug",
        help="Verbose output",
        is_flag=True,
    ),
]

# Very verbose flag
VeryVerboseOpt = Annotated[
    bool,
    typer.Option(
        "-V",
        "--Verbose",
        "--trace",
        help="Very verbose output (trace)",
        is_flag=True,
    ),
]

# Quiet flag
QuietOpt = Annotated[
    bool,
    typer.Option(
        "-q",
        "--quiet",
        help="Quiet mode (minimal output)",
        is_flag=True,
    ),
]

# Very quiet flag
VeryQuietOpt = Annotated[
    bool,
    typer.Option(
        "-Q",
        "--Quiet",
        "--no-output",
        help="Quiet mode (no output)",
        is_flag=True,
    ),
]

#--- Run options ---
# To specify debug in run options
DebugOpt = Annotated[
    bool,
    typer.Option(
        "--debug",
        help="Enable GDB stub if supported",
        is_flag=True,
    ),
]

# To specify the debug port in options
PortOpt = Annotated[
    int,
    typer.Option(
        "-p",
        "--port",
        help="Debug port (implies --debug)",
    ),
]

DockerScreenOpt = Annotated[
    Optional[RunDockerOutputName],
    typer.Option(
        "-s",
        "--screen",
        help="Method to show the screen when using the \"docker\" environment",
        is_flag=True,
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
    "DockerScreenOpt"
]
