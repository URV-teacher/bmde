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

"""Functions called for each subcommand of the CLI.

Each function is responsible for attending a single subcommand with their arguments specified through the function
typehint arguments using Typer. Each function will build a Settings object with the CLI overrides, arguments and default
settings, which will be passed to the function and run a command.
Each function will also be responsible for aborting execution with CLI arguments that are impossible. This only applies
to data coming from the CLI, the syntax of the overrides is not responsibility of the function of these files.
"""

from __future__ import annotations

import typer
from rich.console import Console

import bmde.commands.build.cli
import bmde.commands.check.cli
import bmde.commands.config.cli
import bmde.commands.debug.cli
import bmde.commands.git.cli
import bmde.commands.patch.cli
import bmde.commands.run.cli

# Import modules directly to ensure they are loaded and available
import bmde.core.cli_global

console = Console()
app = typer.Typer(add_completion=False, help="BMDE CLI", no_args_is_help=True)  # TODO Completion does not work

# Use the imported modules directly
app.callback()(bmde.core.cli_global.cli_global_callback)

app.command("build")(bmde.commands.build.cli.build_controller)
app.command("git")(bmde.commands.git.cli.git_controller)
app.command("patch")(bmde.commands.patch.cli.patch_controller)
app.command("run")(bmde.commands.run.cli.run_controller)
app.command("debug")(bmde.commands.debug.cli.debug_controller)
app.command("check")(bmde.commands.check.cli.check_controller)
app.command("config")(bmde.commands.config.cli.config_controller)

if __name__ == "__main__":
    app()
