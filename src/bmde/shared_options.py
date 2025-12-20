"""
Reusable CLI argument definition.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Annotated

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
    )
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
    )
]

# Arguments passed directly to the entrypoint
ArgumentsOpt = Annotated[
    List[str],
    typer.Argument(help="Arguments that are passed to the backend entrypoint.")]

# Argument to send a directory
DirectoryOpt = Annotated[
    Path,
    typer.Option(
        "-d",
        "--directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to a directory. If omitted, the current directory is used."
    )
]



# Path to file that will be used as entrypoint
EntrypointOpt = Annotated[
    Optional[Path],
    typer.Option(
        "--entrypoint",
        help="Override backend entrypoint executable"
    )
]

### Global options
# Dry-run flag
DryRunOpt = Annotated[
    bool,
    typer.Option(
        "--dry-run",
        help="Simulate actions without executing",
        is_flag=True
    )
]

LogFileOpt = Annotated[
    Path,
    typer.Option(
        "-l",
        "--log-file",
        help="Path to log file (optional)")
]

# Verbose flag
VerboseOpt = Annotated[
    bool,
    typer.Option(
        "-v",
        "--verbose",
        "--debug",
        help="Verbose output (debug)",
        is_flag=True
    )
]

# Very verbose flag
VeryVerboseOpt = Annotated[
    bool,
    typer.Option(
        "--t",
        "--trace",
        help="Very verbose output (trace)",
        is_flag=True
    )
]

# Quiet flag
QuietOpt = Annotated[
    bool,
    typer.Option(
        "-q",
        "--quiet",
        help="Quiet mode (minimal output)",
        is_flag=True
    )
]

# Very quiet flag
VeryQuietOpt = Annotated[
    bool,
    typer.Option(
        "-Q",
        "--Quiet",
        "--no-output",
        help="Quiet mode (no output)",
        is_flag=True
    )
]

#--- Run options ---
# To specify debug in run options
DebugOpt = Annotated[
    bool,
    typer.Option(
        "--debug",
        help="Enable GDB stub if supported",
        is_flag=True
    )
]

# To specify the debug port in options
PortOpt = Annotated[
    int,
    typer.Option(
        "-p",
        "--port",
        help="Debug port (implies --debug)"
    )
]

DockerScreenOpt = Annotated[
    Optional[RunDockerOutputName],
    typer.Option(
        "-s",
        "--screen",
        help="Method to show the screen when using the \"docker\" environment",
        is_flag=True
    )
]

NdsRomOpt = Annotated[
    Optional[Path],
    typer.Option(
    None, "-n", "--nds",
    exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True,
    help="Path to the .nds binary (optional). If omitted, searches the current directory."
    )
]

FatImageOpt = Annotated[
    Optional[Path],
    typer.Option(
    None,
        "-i",
        "--image",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to FAT image (optional)"
    )
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
    "BackendOpt",
    "ArgumentsOpt",
    "DirectoryOpt",
    "VeryVerboseOpt",
    "VeryQuietOpt",
    "LogFileOpt",
    "NdsRomOpt",
    "FatImageOpt"
]
