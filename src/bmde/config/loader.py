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

"""Loads the configuration of BMDE.

The sources are, from lowest to highest priority, each one merged key by key over the previous ones:

1. System: /etc/bmde/bmde.toml (on Windows, the bmde folder of ProgramData).
2. User: bmde.toml in the configuration directory of the user (~/.config/bmde on Linux, honouring $XDG_CONFIG_HOME).
3. Project: the nearest bmde.toml from the current directory up to the root of its git repository.
4. Environment variables BMDE_<SECTION>__<KEY>, with __ between every level (e.g. BMDE_RUN__DEBUG=true).
5. The file given with --config.
6. Command line flags, which the commands apply over the loaded settings.

Environment variables beat the files so they work as one-off overrides (BMDE_RUN__DEBUG=true bmde run), and --config
beats them because, like a flag, it is given for this execution only.
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import platformdirs
from pydantic_settings import EnvSettingsSource

from ..core import logging
from ..core.paths import find_upwards
from .schema import Settings

log = logging.get_logger(__name__)

APP_NAME = "bmde"
CONFIG_FILE_NAME = "bmde.toml"
ENV_PREFIX = "BMDE_"


@dataclass(frozen=True)
class ConfigSource:
    """A source of configuration and the values it supplies."""

    name: str
    # File path, or a description of where the source was looked for
    location: str
    found: bool
    data: dict[str, Any]


def system_config_file() -> Path:
    # platformdirs would give /etc/xdg/bmde on Linux; /etc/bmde is where the admin of a lab machine looks for it
    if os.name == "posix":
        return Path("/etc") / APP_NAME / CONFIG_FILE_NAME
    return Path(platformdirs.site_config_dir(APP_NAME, appauthor=False)) / CONFIG_FILE_NAME


def user_config_file() -> Path:
    # roaming: on Windows, %APPDATA% (follows the user across machines of a domain) instead of %LOCALAPPDATA%
    path = Path(platformdirs.user_config_dir(APP_NAME, appauthor=False, roaming=True)) / CONFIG_FILE_NAME
    # Previous versions always used ~/.config/bmde, which is not the user config directory on macOS and Windows or when
    # $XDG_CONFIG_HOME is set
    legacy = Path.home() / ".config" / APP_NAME / CONFIG_FILE_NAME
    if not path.is_file() and legacy != path and legacy.is_file():
        log.warning(f"Reading the user configuration from {legacy}, where previous versions kept it. Move it to {path}")
        return legacy
    return path


def read_toml(path: Path) -> dict[str, Any]:
    """Reads .toml file with its paths and returns a dictionary with its values.

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
        # Only the keys: the values can be credentials, and they are logged before the SecretsFilter knows them (or,
        # when bmde is used as a library, under the filter of the caller, which does not know them at all)
        log.trace(f"Loaded settings: {', '.join(key_paths(settings))}")
        return settings


def key_paths(data: dict[str, Any], prefix: str = "") -> list[str]:
    """Returns the dotted path of every leaf key of a nested dictionary, e.g. ["git.ssh.host", "logging.level"]."""
    paths: list[str] = []
    for key, value in data.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict):
            paths += key_paths(value, prefix=f"{path}.")
        else:
            paths.append(path)
    return paths


def env_config() -> dict[str, Any]:
    """Reads the configuration from the environment variables BMDE_<SECTION>__<KEY>.

    For example, BMDE_RUN__ENVIRONMENT=docker -> env["run"]["environment"] = "docker", with __ between every level of
    nesting. Lists are given as JSON (e.g. BMDE_RUN__EXECUTION_SETTINGS__ARGUMENTS='["--foo"]').

    Returns:
        Nested dictionary with the values of the variables, still as strings except for the JSON ones.

    """
    warn_legacy_env_vars(os.environ)
    result = EnvSettingsSource(Settings)()
    # Only the keys, for the same reason as in read_toml
    log.debug(f"Parsed environment variables: {', '.join(key_paths(result))}")
    return result


def warn_legacy_env_vars(names: Iterable[str]) -> None:
    """Warns about the variables BMDE_<SECTION>_<KEY> of previous versions, which are ignored now."""
    sections = set(Settings.model_fields)
    for name in names:
        upper = name.upper()
        if not upper.startswith(ENV_PREFIX) or "__" in upper:
            continue
        section, _, key = upper[len(ENV_PREFIX) :].partition("_")
        if section.lower() in sections and key:
            log.warning(
                f"{name} is ignored: environment variables need __ after the section and between nested keys, "
                f"e.g. {ENV_PREFIX}{section}__{key}"
            )


def merge(a: dict[Any, Any], b: dict[Any, Any]) -> dict[Any, Any]:
    """Merges the second dictionary b into the first dictionary a.

    Sets the values of the first dictionary a with the values of the second dictionary b for all the coinciding keys.
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


def file_source(name: str, path: Path) -> ConfigSource:
    log.debug(f"Trying to read {name} config from {path}")
    return ConfigSource(name=name, location=str(path), found=path.is_file(), data=read_toml(path))


def config_sources(explicit_config: Path | None = None) -> list[ConfigSource]:
    """Reads every source of configuration (see the docstring of the module).

    Args:
        explicit_config: Path to a run-specific BMDE's TOML configuration file.

    Returns:
        The sources from lowest to highest priority, including the ones that were not found.

    """
    sources = [file_source("system", system_config_file()), file_source("user", user_config_file())]

    start_path = Path.cwd()
    log.debug(f'Trying to find project config "{CONFIG_FILE_NAME}" starting from {start_path} and upwards.')
    project_cfg = find_upwards(CONFIG_FILE_NAME, start=start_path)
    if project_cfg:
        sources.append(file_source("project", project_cfg))
    else:
        searched = f"{CONFIG_FILE_NAME} from {start_path} up to the root of its git repository"
        sources.append(ConfigSource(name="project", location=searched, found=False, data={}))

    log.debug("Trying to read config from environment variables")
    env = env_config()
    sources.append(ConfigSource(name="environment", location=f"{ENV_PREFIX}* variables", found=bool(env), data=env))

    if explicit_config:
        sources.append(file_source("--config", explicit_config))
    return sources


def merge_sources(sources: Iterable[ConfigSource]) -> dict[str, Any]:
    acc: dict[str, Any] = {}
    for source in sources:
        acc = merge(acc, source.data)
    return acc


def load_settings(explicit_config: Path | None = None) -> Settings:
    """Loads the settings from every source (see the docstring of the module).

    The command line flags are NOT applied by this function: the commands apply them over the result.

    Args:
        explicit_config: Path to a run-specific BMDE's TOML configuration file.

    Returns:
        Settings object with the configuration from all subcommands.

    """
    return Settings.model_validate(merge_sources(config_sources(explicit_config)))
