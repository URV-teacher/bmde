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

from dataclasses import dataclass
from pathlib import Path

from bmde.commands.run.spec import RunSpec
from bmde.core.spec import BaseSpec
from bmde.core.spec_opts import SpecExecOpts
from bmde.core.types import DebuggerOptions, DockerOutputOptions


@dataclass
class DebugSpecOpts(BaseSpec):
    elf: Path
    debugger: DebuggerOptions
    docker_screen: DockerOutputOptions | None
    # Emulator to debug, run in debug mode
    RunSpec: RunSpec


@dataclass
class DebugSpec(BaseSpec):
    SpecExecOpts: SpecExecOpts
    DebugSpecOpts: DebugSpecOpts
