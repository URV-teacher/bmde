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

"""Tests of the installation methods of the BMDE (docs/getting-started/installation.md).

Each method is tested as a user follows it, as far as it can be without a display: the components installed with
scripts/install.sh, a project built with the Makefiles that run in Docker, in the full development environment and
with the CLI in Docker, and the CLI installed with pipx (or a venv, which is what pipx does).
"""

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from importlib.metadata import distribution
from pathlib import Path

import pytest

from bmde.core.docker import can_run_docker

REPO = Path(__file__).resolve().parents[2]
INSTALL = REPO / "scripts" / "install.sh"
EXAMPLES = REPO / "examples"
HELLO_WORLD = "https://github.com/URV-teacher/hello-world-nds"


def run(
    args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, check=False)


def require_docker() -> None:
    if not can_run_docker():
        pytest.skip("Docker is not available")


def require_compose() -> None:
    require_docker()
    if run(["docker", "compose", "version"]).returncode != 0:
        pytest.skip("docker compose is not available")


def require_local_image(image: str) -> None:
    # Too big to download in a test: they are tested when they are available (e.g. built with docker buildx bake)
    require_docker()
    if run(["docker", "image", "inspect", image]).returncode != 0:
        pytest.skip(f"{image} is not available locally")


@pytest.fixture(scope="module")
def hello_world_source(tmp_path_factory: pytest.TempPathFactory) -> Path:
    if not shutil.which("git"):
        pytest.skip("git not found")
    source = tmp_path_factory.mktemp("source") / "hello-world-nds"
    subprocess.run(["git", "clone", "--depth", "1", HELLO_WORLD, str(source)], check=True)
    return source


@pytest.fixture
def project(hello_world_source: Path, tmp_path: Path) -> Path:
    """A fresh copy of the hello world project, named hello-world-nds, as the ROM it builds."""
    copy = tmp_path / hello_world_source.name
    shutil.copytree(hello_world_source, copy)
    return copy


def assert_built_by_the_user(project: Path) -> None:
    rom = project / f"{project.name}.nds"
    assert rom.is_file()
    # The containers run with the UID of the user, so the files of the build are not owned by root
    assert rom.stat().st_uid == os.getuid()


# ---- scripts/install.sh (host components: methods 1 and 2) ---------------------------------------------------------


def test_install_script_lists_every_component() -> None:
    result = run([str(INSTALL), "--list"])

    assert result.returncode == 0
    components = [line.split()[0] for line in result.stdout.splitlines()]
    assert components == ["devkitarm", "desmume", "insight", "dlditool", "grit", "git", "vpn", "vscode"]


def test_install_script_installs_in_the_order_of_the_dependencies(tmp_path: Path) -> None:
    # grit after devkitARM (which it copies), whatever the order of the arguments
    result = run([str(INSTALL), "--dry-run", "grit", "devkitarm"], env={**os.environ, "BMDE_ROOT": str(tmp_path)})

    assert result.returncode == 0
    scripts = [Path(line.split()[-1]).name for line in result.stdout.splitlines() if line.startswith("+ bash ")]
    assert scripts == [
        "install_make.sh",
        "install_devkitarm.sh",
        "install_libnds.sh",
        "install_examples.sh",
        "install_grit.sh",
    ]
    # The assets of each component are downloaded before its install scripts
    assert "devkitarm-nds-docker/scripts/download_assets.sh devkitARM_r46-x86_64-linux.tar.bz2" in result.stdout


def test_install_script_rejects_unknown_components() -> None:
    result = run([str(INSTALL), "devkitarm", "notepad"])

    assert result.returncode != 0
    assert "unknown component notepad" in result.stderr


def test_install_script_downloads_the_docker_images() -> None:
    require_docker()

    result = run([str(INSTALL), "--docker", "--dry-run", "desmume", "git"], env={**os.environ, "BMDE_TAG": "1.2.3"})

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "+ docker pull aleixmt/desmume:1.2.3",
        "+ docker pull aleixmt/git-sshpass:1.2.3",
    ]


def test_install_script_installs_components_in_a_host() -> None:
    """Installs dlditool and git in a clean Ubuntu (the base image), as root, from the script alone.

    BMDE_COMPONENTS_DIR is empty, so the script also clones the components, as when it runs outside of a checkout.
    """
    require_docker()
    script = (
        "/bmde/scripts/install.sh dlditool git"
        " && bash --login -c 'dlditool > /dev/null; command -v git git.exp && ls /URV/bmde/dlditool/dldi'"
    )

    result = run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{INSTALL.parent}:/bmde/scripts:ro",
            "-e",
            "BMDE_COMPONENTS_DIR=/components",
            "--entrypoint",
            "bash",
            "aleixmt/bmde-base:latest",
            "-c",
            script,
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "/URV/bmde/git-urv-vpn/bin/git.exp" in result.stdout
    assert "mpcf.dldi" in result.stdout


# ---- Makefiles with Docker (method 5) ------------------------------------------------------------------------------


def make_dry_run(project: Path, target: str, env: dict[str, str] | None = None) -> str:
    environment = {k: v for k, v in os.environ.items() if k not in ("DEVKITARM", "DEVKITPRO", "DESMUME", "DOCKER_FLAG")}
    result = run(["make", "-n", target], cwd=project, env={**environment, **(env or {})})
    assert result.returncode == 0, result.stderr
    return result.stdout


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    if not shutil.which("make"):
        pytest.skip("make not found")
    directory = tmp_path / "game"
    directory.mkdir()
    return directory


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("build", ["aleixmt/bmde-linux:latest", "DOCKER_FLAG=1", "--user"]),
        ("clean", ["aleixmt/bmde-linux:latest clean"]),
        ("run", ["aleixmt/desmume:latest /roms/game.nds"]),
        (
            "debug",
            ["--arm9gdb=1000 /roms/game.nds", "GDB_TARGET=bmde-desmume-game:1000", "aleixmt/insight:latest game.elf"],
        ),
    ],
)
def test_docker_makefile_runs_each_target_in_its_image(empty_project: Path, target: str, expected: list[str]) -> None:
    shutil.copy(EXAMPLES / "makefile-docker" / "Makefile", empty_project)

    commands = make_dry_run(empty_project, target)

    for text in expected:
        assert text in commands


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("build", ["PROJECT=game", "run --rm build\n"]),
        ("clean", ["run --rm build clean"]),
        ("run", ["run --rm -d --name bmde-desmume-game desmume /roms/game.nds"]),
        (
            "debug",
            ["desmume --arm9gdb=1000 /roms/game.nds", "GDB_TARGET=bmde-desmume-game:1000", "run --rm insight game.elf"],
        ),
    ],
)
def test_compose_makefile_runs_each_target_in_its_service(
    empty_project: Path, target: str, expected: list[str]
) -> None:
    shutil.copy(EXAMPLES / "makefile-compose" / "Makefile", empty_project)

    commands = make_dry_run(empty_project, target)

    for text in expected:
        assert text in commands


@pytest.mark.parametrize("variant", ["makefile-docker", "makefile-compose"])
def test_docker_makefiles_use_the_installed_tools(empty_project: Path, variant: str) -> None:
    # As in a host with the components installed, or in the full development environment
    devkitarm = empty_project.parent / "devkitARM"
    devkitarm.mkdir()
    (devkitarm / "ds_rules").write_text("")
    shutil.copy(EXAMPLES / variant / "Makefile", empty_project)

    commands = make_dry_run(empty_project, "build", {"DEVKITARM": str(devkitarm), "DEVKITPRO": "/", "DESMUME": "/"})

    assert "docker run" not in commands
    assert "docker compose" not in commands
    assert f"make --no-print-directory -C build -f {empty_project}/Makefile" in commands


@pytest.mark.parametrize("variant", ["makefile-docker", "makefile-compose"])
def test_docker_makefiles_build_a_project(project: Path, variant: str) -> None:
    if variant == "makefile-compose":
        require_compose()
    else:
        require_docker()
    if not shutil.which("make"):
        pytest.skip("make not found")
    for file in (EXAMPLES / variant).iterdir():
        shutil.copy(file, project)
    environment = {k: v for k, v in os.environ.items() if k not in ("DEVKITARM", "DOCKER_FLAG")}

    try:
        result = run(["make"], cwd=project, env=environment)
    finally:
        if variant == "makefile-compose":
            run(["docker", "compose", "down", "--volumes"], cwd=project)

    assert result.returncode == 0, result.stdout + result.stderr
    assert_built_by_the_user(project)


# ---- Compose files ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("compose_file", "env"),
    [
        (REPO / "compose.cli.yml", {"DOCKER_GID": "999", "XDG_RUNTIME_DIR": "/run/user/1000"}),
        (EXAMPLES / "shell" / "compose.yml", {}),
        (EXAMPLES / "makefile-compose" / "compose.yml", {}),
        (REPO / "shell" / "compose.yml", {}),
    ],
)
def test_compose_files_are_valid(compose_file: Path, env: dict[str, str]) -> None:
    require_compose()

    result = run(["docker", "compose", "-f", str(compose_file), "config", "--quiet"], env={**os.environ, **env})

    assert result.returncode == 0, result.stderr


# ---- Development environment in Docker (method 3) ------------------------------------------------------------------


def test_full_environment_builds_a_project_with_docker_run(project: Path) -> None:
    require_local_image("aleixmt/bmde-full:latest")
    mount = f"/home/bmde/{project.name}"

    result = run(["docker", "run", "--rm", "-v", f"{project}:{mount}", "-w", mount, "aleixmt/bmde-full:latest", "make"])

    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / f"{project.name}.nds").is_file()


def test_full_environment_builds_a_project_with_compose(project: Path, tmp_path: Path) -> None:
    require_local_image("aleixmt/bmde-full:latest")
    require_compose()
    if not Path("/dev/ppp").exists():
        pytest.skip("/dev/ppp, which the template gives to the container for the VPN, is not available")
    shutil.copy(EXAMPLES / "shell" / "compose.yml", project)
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    env = {**os.environ, "BMDE_SECRETS_DIR": str(secrets), "PROJECT": project.name}

    try:
        result = run(["docker", "compose", "run", "--rm", "-T", "shell", "make"], cwd=project, env=env)
    finally:
        # Only the network: the volume with the settings of DeSmuME and VS Code is shared by every project
        run(["docker", "compose", "down"], cwd=project, env=env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / f"{project.name}.nds").is_file()


# ---- The bmde CLI in Docker (method 4) -----------------------------------------------------------------------------


@pytest.fixture
def cli_compose_env(tmp_path: Path) -> Iterator[dict[str, str]]:
    require_local_image("aleixmt/bmde:latest")
    require_compose()
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime_dir or not Path(runtime_dir).is_dir():
        pytest.skip("XDG_RUNTIME_DIR, which the CLI in Docker mounts, is not available")
    config = tmp_path / "config"
    (config / "bmde").mkdir(parents=True)
    yield {
        **os.environ,
        "BMDE_UID": str(os.getuid()),
        "BMDE_GID": str(os.getgid()),
        "DOCKER_GID": str(Path("/var/run/docker.sock").stat().st_gid),
        "XDG_CONFIG_HOME": str(config),
    }
    run(["docker", "compose", "-f", str(REPO / "compose.cli.yml"), "down"])


@pytest.mark.parametrize("backend", ["docker", "host"])
def test_cli_in_docker_builds_a_project(project: Path, cli_compose_env: dict[str, str], backend: str) -> None:
    # docker: the CLI runs aleixmt/bmde-linux with the Docker of the host; host: the devkitARM of the image of the CLI
    result = run(
        [
            "docker",
            "compose",
            "-f",
            str(REPO / "compose.cli.yml"),
            "run",
            "--rm",
            "-T",
            "bmde",
            "build",
            "--no-interactive",
            "--backend",
            backend,
        ],
        cwd=project,
        env={**cli_compose_env, "PWD": str(project)},
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert_built_by_the_user(project)


# ---- The bmde CLI (method 1) and from the sources (method 6) -------------------------------------------------------


def test_cli_installs_with_pipx(tmp_path: Path) -> None:
    """Installs the package of this checkout as a user does, with pipx, or else in a venv (which is what pipx does)."""
    if shutil.which("pipx"):
        env = {**os.environ, "PIPX_HOME": str(tmp_path / "pipx"), "PIPX_BIN_DIR": str(tmp_path / "bin")}
        install = run(["pipx", "install", str(REPO)], env=env)
        bmde = tmp_path / "bin" / "bmde"
    else:
        venv = tmp_path / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        install = run([str(venv / "bin" / "pip"), "install", str(REPO)])
        bmde = venv / "bin" / "bmde"
    assert install.returncode == 0, install.stdout + install.stderr

    result = run([str(bmde), "--version"])

    assert result.returncode == 0
    assert result.stdout.startswith("bmde ")


def test_development_install_runs_the_checkout() -> None:
    # make dev (and make install-test of CI) install the checkout in editable mode, so bmde runs its code
    direct_url = distribution("bmde").read_text("direct_url.json")
    if direct_url is None:
        pytest.skip("bmde is not installed from a checkout")

    origin = json.loads(direct_url)

    assert origin["dir_info"].get("editable") is True
    assert Path(origin["url"].removeprefix("file://")) == REPO
