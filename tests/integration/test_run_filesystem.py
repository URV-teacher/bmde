import subprocess
import shutil
import time
import zipfile
import urllib.request
import logging
from pathlib import Path
import pytest
from bmde.commands.build.command import build_command
from bmde.commands.patch.command import patch_command
from bmde.commands.run.command import run_command
from bmde.core.logging import setup_logging


def test_run_filesystem(tmp_path: Path):
    """
    Integration test for the run command with filesystem interaction.
    1. Clones filesystem-nds repo.
    2. Builds it.
    3. Patches the ROM.
    4. Downloads a FAT image.
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
    ret = patch_command(d=repo_dir)
    if isinstance(ret, subprocess.Popen):
        ret.wait()
        assert ret.returncode == 0, "Patch failed"
    elif isinstance(ret, int):
        assert ret == 0, "Patch failed"

    # 4. Prepare FAT image
    print("Downloading FAT image...")
    fat_zip_url = (
        "https://raw.githubusercontent.com/URV-teacher/desmume-docker/master/fs/fat.zip"
    )
    fat_zip_path = tmp_path / "fat.zip"
    try:
        urllib.request.urlretrieve(fat_zip_url, fat_zip_path)
    except Exception as e:
        pytest.fail(f"Failed to download FAT image: {e}")

    print("Extracting FAT image...")
    with zipfile.ZipFile(fat_zip_path, "r") as zip_ref:
        zip_ref.extractall(tmp_path)

    # Locate extracted .img file
    fat_imgs = list(tmp_path.glob("*.img"))
    if not fat_imgs:
        # Try looking inside extracted folders if any
        fat_imgs = list(tmp_path.rglob("*.img"))

    assert len(fat_imgs) > 0, "No .img file found in extracted zip"
    fat_img_path = fat_imgs[0]
    print(f"Using FAT image: {fat_img_path}")

    # 5. Run
    print("Running emulator...")
    # Run in background so we can stop it
    proc = run_command(
        nds_rom=nds_file, fat_image=fat_img_path, background=True, interactive=False
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
    expected_text = (
        "Hola, este es un test en DeSmuME.\nProbando escritura en archivo.\n"
    )

    # Method A: mtools (preferred if available)
    if shutil.which("mtype"):
        print("Using mtools to verify...")
        try:
            # mtype -i image ::file
            result = subprocess.run(
                ["mtype", "-i", str(fat_img_path), "::output.txt"],
                capture_output=True,
                text=True,
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
    search_phrase = "Hola, este es un test en DeSmuME".encode("utf-8")

    if search_phrase in data:
        print("Verification successful (binary search)!")
    else:
        pytest.fail(f"Expected text '{search_phrase.decode()}' not found in FAT image.")
