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
from logging import Logger
from pathlib import Path
from typing import Any, cast

from rich.logging import RichHandler

from bmde.config.schema import Settings
from bmde.core.types import DATE_FORMAT, LogLevel, get_default_log_path

# ---- extend the logging module with TRACE
TRACE_LEVEL_NUM = 1
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
MESSAGE_FORMAT = "%(asctime)s | %(name)s | %(message)s"


class ExtendedLogger(logging.Logger):
    def trace(self: Logger, message: str, *args: Any, **kwargs: Any) -> None:
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


# Tell the logging system to use your new class
logging.setLoggerClass(ExtendedLogger)


class SecretsFilter(logging.Filter):
    def __init__(self, secrets: list[str | None] | None):
        super().__init__()
        self.secrets: list[str | None] = secrets or []

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.secrets:
            return True

        # The secrets can be in the arguments of the message too (e.g. the command of run_cmd, logged with "%s"), so
        # the message is masked once formatted
        message = record.getMessage()
        masked = message
        for secret in self.secrets:
            if secret:
                masked = masked.replace(secret, "*****")
        if masked != message:
            record.msg = masked
            record.args = None
        return True


def setup_logging(
    level: int | None | None,
    log_file: str | Path | None = None,
    secrets: list[str | None] | None = None,
) -> None:
    # Default level is INFO
    if level is None:
        level = logging.INFO

    handlers: list[logging.Handler] = []
    secrets_filter = SecretsFilter(secrets)

    # ---- console (Rich)
    console = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=False,
        show_level=True,
        show_path=False,
    )
    common_formatter = logging.Formatter(MESSAGE_FORMAT, DATE_FORMAT)
    console.setLevel(level)
    console.setFormatter(common_formatter)
    console.addFilter(secrets_filter)
    handlers.append(console)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(common_formatter)
        file_handler.addFilter(secrets_filter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,  # root captures everything
        handlers=handlers,
        format=MESSAGE_FORMAT,
        force=True,
    )


def obfuscate_text(text: str | None) -> str:
    if text is None:
        return str(text)
    else:
        return "*****"


def get_logger(name: str) -> ExtendedLogger:
    """Return a logger with trace() method available."""
    return cast(ExtendedLogger, logging.getLogger(name))


def process_log_flags(very_verbose: bool, verbose: bool, quiet: bool, very_quiet: bool) -> tuple[LogLevel | None, bool]:
    more_than_one_flag = False
    flag_counter = 0
    for flag in (very_verbose, verbose, quiet, very_quiet):
        if flag:
            flag_counter += 1
    if flag_counter > 1:
        more_than_one_flag = True

    if very_verbose:
        return LogLevel.TRACE, more_than_one_flag
    elif verbose:
        return LogLevel.DEBUG, more_than_one_flag
    elif quiet:
        return LogLevel.WARNING, more_than_one_flag
    elif very_quiet:
        return LogLevel.QUIET, more_than_one_flag
    else:
        return None, more_than_one_flag


def configure_logging_from_settings(settings: Settings) -> None:
    if settings.logging.file is None:
        settings.logging.file = get_default_log_path()

    if settings.logging.level is None:
        settings.logging.level = LogLevel.get_default_log_level()

    # Always obfuscate all passwords
    words_to_obfuscate = [settings.git.vpn.password, settings.git.ssh.password]
    # Optionally but by default true obfuscate other sensible data.
    if settings.logging.hide_sensibles:
        words_to_obfuscate += [
            settings.git.git.name,
            settings.git.git.email,
            settings.git.ssh.host,
            settings.git.ssh.username,
            settings.git.vpn.host,
            # An unset port would hide every "None" of the logs
            str(settings.git.vpn.port) if settings.git.vpn.port is not None else None,
            settings.git.vpn.username,
            settings.git.vpn.cert,
            settings.git.vpn.realm,
            settings.git.vpn.test_dns,
            settings.git.vpn.test_ip,
        ]

    setup_logging(
        level=settings.logging.level.to_logging_level(),
        log_file=settings.logging.file,
        secrets=words_to_obfuscate,
    )  # Preventive creation of log for logging the loading of settings
