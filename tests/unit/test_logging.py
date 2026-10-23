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
import sys
from pathlib import Path

import pytest

from bmde.config.schema import Settings
from bmde.core.logging import configure_logging_from_settings


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="XDG_STATE_HOME is only honoured on Linux")
def test_default_log_file_goes_to_the_user_state_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cwd = tmp_path / "repo"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    settings = Settings()
    settings.logging.file = None

    configure_logging_from_settings(settings)
    # Close the file handler, so it does not leak into the other tests
    logging.basicConfig(handlers=[logging.NullHandler()], force=True)

    assert list(cwd.iterdir()) == []
    (log_file,) = (tmp_path / "state" / "bmde" / "log").iterdir()
    # Windows does not allow colons in file names
    assert ":" not in log_file.name
