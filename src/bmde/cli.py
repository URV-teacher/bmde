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

import typer
from rich.console import Console

console = Console()
app = typer.Typer(
    add_completion=False, help="BMDE CLI", no_args_is_help=True
)  # TODO Completion does not work
