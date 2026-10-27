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

from bmde.commands.build.command import build_command  # noqa: F401
from bmde.commands.git.command import git_command  # noqa: F401
from bmde.commands.patch.command import patch_command  # noqa: F401
from bmde.commands.run.command import run_command  # noqa: F401

# Lets callers read the configuration bmde resolves (e.g. the SSH host and user of git), to build on top of it
from bmde.config.loader import load_settings  # noqa: F401
