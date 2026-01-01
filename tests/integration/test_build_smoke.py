import subprocess
import shutil
import logging
from pathlib import Path
import pytest
from bmde.commands.build.command import build_command
from bmde.core.logging import setup_logging

def test_build_smoke(tmp_path: Path):
    """
    Smoke test for the build command.
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
    
    ret = build_command(d=repo_dir)
    
    ret_code = 0
    if isinstance(ret, int):
        ret_code = ret
    else:
        # It's a Popen object
        ret.communicate()
        ret_code = ret.returncode
        
    assert ret_code == 0, "Build failed with non-zero exit code"
