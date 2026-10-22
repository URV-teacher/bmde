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

from bmde.commands.build.service import BuildService
from bmde.core.types import BackendOptions


def test_build_service_initialization():
    """Verify that BuildService maps the correct backends."""
    service = BuildService()
    # Check if 'host' is in the mapping keys
    assert "host" in [key.value for key in service.mapping]


def test_choose_backend_force_env():
    """Verify that passing an env overrides the default order."""
    service = BuildService()
    # Assuming 'host' is a valid Enum value
    backends = service.choose_backend(BackendOptions.DOCKER)
    assert len(backends) == 1
