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

from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
RULE = "#" + "-" * 81
# Start and end of the branch with the Makefile of the course, used in the containers and with the tools installed
COURSE_START = f"{RULE}\n# In the containers, or with the tools installed: the Makefile of the course\n{RULE}\n"
COURSE_END = f"{RULE}\nendif\n{RULE}\n"


@pytest.mark.parametrize("variant", ["makefile-docker", "makefile-compose"])
def test_docker_makefiles_embed_the_makefile_of_the_course(variant: str) -> None:
    makefile = (EXAMPLES / variant / "Makefile").read_text()
    course = (EXAMPLES / "Makefile").read_text()

    embedded = makefile.split(COURSE_START, 1)[1].removesuffix(COURSE_END)

    assert embedded == course
