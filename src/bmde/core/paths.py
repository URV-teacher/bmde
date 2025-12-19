from pathlib import Path
from typing import Optional, Iterable


def find_upwards(name: str, start: Path) -> Optional[Path]:
    """
    Finds a file with the given name in the start path and in all of its predecessors and returns its path. If not,
    returns None.

    Args:
        name: Name of the desired file.
        start: Directory where the function start looking for the file.

    Returns:
        The path file or None if no such file exists.
    """
    cur = start.resolve()
    root = cur.anchor
    while True:
        candidate = cur / name
        if candidate.exists():
            return candidate
        if str(cur) == root:
            return None
        cur = cur.parent


def find_first(paths: Iterable[Path], pattern: str) -> Optional[Path]:
    for p in paths:
        for hit in p.glob(pattern):
            return hit
    return None
