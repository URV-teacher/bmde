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

import logging
import shutil
import subprocess
from pathlib import Path

import pytest

from bmde.commands.build.command import build_command
from bmde.core.logging import setup_logging


def test_build_smoke(tmp_path: Path):
    """Smoke test for the build command.
    Clones a hello-world repo and attempts to build it.
    This is an integration test.
    """
    # Setup logging to see output
    setup_logging(level=logging.DEBUG)

    # Check prerequisites
    if not shutil.which("git"):
        pytest.skip("git not found")

    repo_url = "https://github.com/URV-teacher/hello-world-nds"
    repo_dir = tmp_path / "hello-world-nds"

    print(f"Cloning {repo_url} into {repo_dir}...")
    # Clone repo
    try:
        # Removed capture_output=True to let git output be seen (with pytest -s)
        subprocess.run(["git", "clone", repo_url, str(repo_dir)], check=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to clone repo: {e}")

    # Run build command
    # We call the API directly to avoid CLI overhead
    print(f"Building in {repo_dir}")

    ret = build_command(d=repo_dir, interactive=False)

    ret_code = 0
    if isinstance(ret, int):
        ret_code = ret
    else:
        # It's a Popen object
        ret.communicate()
        ret_code = ret.returncode

    assert ret_code == 0, "Build failed with non-zero exit code"
