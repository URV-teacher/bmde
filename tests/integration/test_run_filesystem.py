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
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

from bmde.commands.build.command import build_command
from bmde.commands.patch.command import patch_command
from bmde.commands.run.command import run_command
from bmde.core.logging import setup_logging
from bmde.core.types import DockerOutputOptions


# One end-to-end scenario, read top to bottom: split into helpers it would be harder to follow
def test_run_filesystem(tmp_path: Path):  # noqa: PLR0912, PLR0915
    """Integration test for the run command with filesystem interaction.
    1. Clones filesystem-nds repo.
    2. Builds it.
    3. Patches the ROM.
    4. Creates an empty FAT image.
    5. Runs the ROM with the FAT image.
    6. Verifies output.txt is written to the FAT image.
    """
    setup_logging(level=logging.DEBUG)

    # Prerequisites
    if not shutil.which("git"):
        pytest.skip("git not found")

    # 1. Clone
    repo_url = "https://github.com/URV-teacher/filesystem-nds"
    repo_dir = tmp_path / "filesystem-nds"
    print(f"Cloning {repo_url}...")
    subprocess.run(["git", "clone", repo_url, str(repo_dir)], check=True)

    # 2. Build
    print("Building...")
    ret = build_command(d=repo_dir, interactive=False)
    if isinstance(ret, subprocess.Popen):
        ret.wait()
        assert ret.returncode == 0, "Build failed"
    elif isinstance(ret, int):
        assert ret == 0, "Build failed"

    # Find .nds file
    nds_files = list(repo_dir.glob("*.nds"))
    assert len(nds_files) > 0, "No .nds file found after build"
    nds_file = nds_files[0]
    print(f"Found ROM: {nds_file}")

    # 3. Patch
    print("Patching...")
    ret = patch_command(d=repo_dir, interactive=False)
    if isinstance(ret, subprocess.Popen):
        ret.wait()
        assert ret.returncode == 0, "Patch failed"
    elif isinstance(ret, int):
        assert ret == 0, "Patch failed"

    # 4. Prepare FAT image: an empty one, created by the script of desmume-docker (submodule)
    create_fat_image = Path(__file__).resolve().parents[2] / "components/desmume-docker/scripts/create_fat_image.sh"
    if not create_fat_image.is_file():
        pytest.skip(f"{create_fat_image} not found (submodule components/desmume-docker not checked out)")
    if not shutil.which("mkfs.fat"):
        pytest.skip("mkfs.fat not found (package dosfstools)")
    print("Creating FAT image...")
    fat_img_path = tmp_path / "fat.img"
    subprocess.run([str(create_fat_image), str(fat_img_path)], check=True)
    # The emulator in the container runs as another user and writes to the image
    os.chmod(fat_img_path, 0o777)  # noqa: S103
    print(f"Using FAT image: {fat_img_path}")

    # 5. Run
    print("Running emulator...")
    # Run in background so we can stop it
    proc = run_command(
        nds_rom=nds_file,
        fat_image=fat_img_path,
        interactive=False,
        graphical_output=DockerOutputOptions.VNC,
    )

    # Wait for emulation to start and write to file
    # The ROM is simple, it should write quickly.
    time.sleep(10)

    # Terminate emulator
    if isinstance(proc, subprocess.Popen):
        print("Terminating emulator...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    # 6. Verify content
    print("Verifying output...")
    expected_text = "Hola, este es un test en DeSmuME.\nProbando escritura en archivo.\n"

    # Method A: mtools (preferred if available)
    if shutil.which("mtype"):
        print("Using mtools to verify...")
        try:
            # mtype -i image ::file
            result = subprocess.run(
                ["mtype", "-i", str(fat_img_path), "::output.txt"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                content = result.stdout
                # Normalize newlines just in case
                if expected_text in content:
                    print("Verification successful (mtools)!")
                    return
                else:
                    print(f"Content mismatch via mtools. Got: {content!r}")
            else:
                print(f"mtype failed: {result.stderr}")
        except Exception as e:
            print(f"mtools check failed: {e}")

    # Method B: Binary search (Fallback)
    print("Using binary search to verify...")
    with open(fat_img_path, "rb") as f:
        data = f.read()

    # The text in the file might use \n or \r\n. The expected string has \n.
    # We search for the main sentence.
    search_phrase = b"Hola, este es un test en DeSmuME"

    if search_phrase in data:
        print("Verification successful (binary search)!")
    else:
        pytest.fail(f"Expected text '{search_phrase.decode()}' not found in FAT image.")
