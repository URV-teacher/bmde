import typer

from bmde.cli import app
from bmde.config.loader import load_settings
from bmde.core import logging
from bmde.core.logging import LogLevel, setup_logging, get_default_log_path
from bmde.core.shared_options import (
    ConfigOpt,
    VerboseOpt,
    VeryVerboseOpt,
    QuietOpt,
    VeryQuietOpt,
    LogFileOpt,
)

log = logging.get_logger(__name__)


@app.callback()
def _global(
    ctx: typer.Context,
    config: ConfigOpt = None,
    verbose: VerboseOpt = False,
    very_verbose: VeryVerboseOpt = False,
    quiet: QuietOpt = False,
    very_quiet: VeryQuietOpt = False,
    log_file: LogFileOpt = None,
) -> None:
    """
    Global option callback. Executed if no command is provided.
    """
    # Preventive creation of logger if CLI options are provided before loading settings
    if very_verbose is True:
        cli_log_level = LogLevel.TRACE
    elif verbose is True:
        cli_log_level = LogLevel.DEBUG
    elif quiet is True:
        cli_log_level = LogLevel.WARNING
    elif very_quiet is True:
        cli_log_level = LogLevel.QUIET
    else:
        cli_log_level = None

    if cli_log_level is not None:
        preventive_log_level = cli_log_level.to_logging_level()
    else:
        preventive_log_level = LogLevel.INFO.to_logging_level()

    if log_file is None:
        preventive_log_file = get_default_log_path()
    else:
        preventive_log_file = log_file

    setup_logging(
        preventive_log_level, log_file=preventive_log_file
    )  # Preventive creation of log for logging the loading of settings

    flag_counter = 0
    for flag in (very_verbose, verbose, quiet, very_quiet):
        if flag is True:
            flag_counter += 1
    if flag_counter > 1:
        log.warning(
            "You can not use more than one verbosity flag at the same time. The most verbose flag you specified "
            "will be applied."
        )
    # Load settings
    settings = load_settings(explicit_config=config)

    # CLI overrides
    if log_file is not None:
        settings.logging.file = log_file
    if cli_log_level is not None:  # CLI specifies a logging level
        settings.logging.level = cli_log_level

    # Global logging setup
    setup_logging(
        LogLevel(settings.logging.level).to_logging_level(),
        log_file=settings.logging.file,
    )

    # Load settings into global context
    ctx.obj = {"settings": settings}
    log.debug("Ended global callback")
