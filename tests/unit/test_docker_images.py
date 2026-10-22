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

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from bmde.config.loader import load_settings
from bmde.config.schema import Settings
from bmde.core import docker
from bmde.core.docker import configure_docker_from_settings, docker_image


@pytest.fixture(autouse=True)
def unconfigured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """No bmde.toml or BMDE_ variable of the machine, and no tag configured by another test."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    for name in list(os.environ):
        if name.startswith("BMDE_"):
            monkeypatch.delenv(name)
    yield
    configure_docker_from_settings(Settings())


@pytest.mark.parametrize(
    ("installed", "tag"),
    [("1.15.0", "1.15.0"), ("1.14.1.dev3+g1234567", "latest"), ("2.0.0rc1", "latest")],
)
def test_images_follow_the_installed_release(monkeypatch: pytest.MonkeyPatch, installed: str, tag: str) -> None:
    monkeypatch.setattr(docker, "version", lambda _: installed)
    assert docker_image("desmume") == f"aleixmt/desmume:{tag}"


def test_image_tag_setting_pins_every_image(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(docker, "version", lambda _: "1.15.0")
    monkeypatch.setenv("BMDE_DOCKER__IMAGE_TAG", "sha-0123abc")

    configure_docker_from_settings(load_settings())

    assert docker_image("insight") == "aleixmt/insight:sha-0123abc"
    assert docker_image("bmde-linux") == "aleixmt/bmde-linux:sha-0123abc"
