from collections.abc import Iterable
from pathlib import Path


def find_git_root(start: Path) -> Path | None:
    """
    Returns the root of the git repository that contains start (the directory with the .git folder, or the .git file of
    a submodule or worktree), or None if start is not inside a git repository.
    """
    cur = start.resolve()
    for directory in (cur, *cur.parents):
        if (directory / ".git").exists():
            return directory
    return None


def find_upwards(name: str, start: Path) -> Path | None:
    """
    Finds a file with the given name in the start path and in its predecessors and returns its path. If not, returns
    None.

    The search stops at the root of the git repository that contains start, and never looks in the home directory of
    the user or above it, so a stray ~/bmde.toml is not taken as the file of every project below it.

    Args:
        name: Name of the desired file.
        start: Directory where the function start looking for the file.

    Returns:
        The path file or None if no such file exists.
    """
    home = Path.home().resolve()
    cur = start.resolve()
    while not home.is_relative_to(cur):
        candidate = cur / name
        if candidate.is_file():
            return candidate
        if (cur / ".git").exists() or cur == cur.parent:
            return None
        cur = cur.parent
    return None


def find_first(paths: Iterable[Path], pattern: str) -> Path | None:
    for p in paths:
        for hit in p.glob(pattern):
            return hit
    return None
