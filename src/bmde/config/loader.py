from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from .schema import Settings
from ..core import logging
from ..core.paths import find_upwards

log = logging.get_logger(__name__)


def read_toml(path: Path) -> dict[str, str]:
    """
    Reads .toml file with its paths and returns a dictionary with its values.

    Args:
        path: Path of the TOML file.

    Returns: Plain dictionary with the key-values of the TOML file.

    """
    if not path or not path.is_file():
        log.debug(f"File {path} not found or not a valid file")
        return {}
    with path.open("rb") as f:
        log.debug(f"Reading TOML file: {path}")
        settings = tomllib.load(f)
        log.trace(f"Loaded settings: {settings}")
        return settings


def env_config(prefix: str = "TOT_") -> dict[str, dict[str, str]]:
    """
    Reads the configuration from the environment and returns it as a nested dictionary of the read subcommands.

    Args:
        prefix: The prefix that the system variables must have to be added to the dictionary.

    Returns:
        Nested dictionary. The first key is the word after the first _ of the name of the system variable in lowercase,
        which represents the subcommand name (run, build...) and the second key is the rest of the name of the system
        variable in lowercase. The value is the value of the property. (e.g., TOT_RUN_ENVIRONMENT=docker -->
        env[RUN][ENVIRONMENT] = docker)

    """
    result: dict[str, dict[str, str]] = {}
    for k, v in os.environ.items():
        if not k.startswith(prefix):
            continue
        parts = k[len(prefix) :].lower().split("_")
        if len(parts) >= 2:
            section, key = parts[0], "_".join(parts[1:])
            if section not in result.keys():
                result[section] = {}
            result[section][key] = v
    log.debug(f"Parsed environment variables: {str(result)}")
    return result


def merge(a: dict[Any, Any], b: dict[Any, Any]) -> dict[Any, Any]:
    """
    Merges two dictionaries by setting the values of the first dictionary a with the values of the second dictionary b
    for all the coinciding keys.
    If the values for the same key in the two dictionaries are also dictionaries, perform recursive call to merge those
    in the same way.

    Args:
        a: The first dictionary to merge.
        b: The second dictionary to merge.

    Returns:
        The merged dictionary.
    """
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = v
    return out


def load_settings(explicit_config: Path | None = None) -> Settings:
    """
    Loads settings following the priority:
    1. Environment variables: Variables prefixed with TOT_ENVIRONMENT
    2. /etc/bmde/bmde.toml
    3. ~/.config/bmde/bmde.toml
    4. bmde.toml from the repository
    5. Explicit config given via arguments

    This behaviour is NOT performed by this function but for completion we must say that settings with priority 6 would
    come from CLI arguments.

    Args:
        explicit_config: Path to a run-specific TOT's TOML configuration file.

    Returns:
        Settings object with the configuration from all subcommands.

    """
    # 1) system env (lowest)
    log.debug("Trying to read global config from Environment Variables")
    acc = env_config()

    global_paths = [
        Path("/etc/bmde/bmde.toml"),  # 2) system-wide global config
        Path(
            os.path.expanduser("~/.config/bmde/bmde.toml")
        ),  # 3) user-specific global config
    ]
    for gp in global_paths:
        log.debug(f"Trying to read global config from {gp}")
        acc = merge(acc, read_toml(gp))

    # 4) repo config (closest bmde.toml up-tree)
    start_path = Path.cwd()
    log.debug(
        f'Trying to find repo config "bmde.toml" starting from {start_path} and upwards.'
    )
    repo_cfg = find_upwards("bmde.toml", start=start_path)
    if repo_cfg:
        log.debug(f"Trying to read repo config found in {repo_cfg}")
        acc = merge(acc, read_toml(repo_cfg))

    # 5) execution-specific config (highest)
    if explicit_config:
        log.debug(f"Trying to read explicit CLI config from {explicit_config}")
        acc = merge(acc, read_toml(explicit_config))

    return Settings.model_validate(acc)
