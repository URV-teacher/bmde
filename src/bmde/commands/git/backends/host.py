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

import shutil
import subprocess

from bmde.core import logging
from bmde.core.exec import ExecOptions, run_cmd
from bmde.core.os_utils import is_command_available

from ..spec import GitSpecOpts
from .backend import GitBackend

log = logging.get_logger(__name__)


class HostRunner(GitBackend):
    def is_available(self) -> bool:
        return is_command_available("git")

    # The host git only takes the arguments of exec_opts, but the signature is the one of every Backend
    def run(self, spec: GitSpecOpts, exec_opts: ExecOptions) -> int | subprocess.Popen[bytes]:  # noqa: ARG002
        entry = str(exec_opts.entrypoint) if exec_opts.entrypoint else (shutil.which("git"))
        if not entry:
            return 127
        args = [entry]
        if exec_opts.arguments is not None:
            args += list(exec_opts.arguments)
        log.debug("Arguments for git in host backend: " + str(args))
        return run_cmd(args, exec_opts)
