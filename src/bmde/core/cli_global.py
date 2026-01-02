import typer

from bmde.cli import app
from bmde.config.loader import load_settings
from bmde.core import logging
from bmde.core.logging import (
    process_log_flags,
    configure_logging_from_settings,
)
from bmde.core.shared_options import (
    ConfigOpt,
    VerboseOpt,
    VeryVerboseOpt,
    QuietOpt,
    VeryQuietOpt,
    LogFileOpt,
    ShowConfigOpt,
    ShowDefaultConfigOpt,
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
    show_config: ShowConfigOpt = False,
    show_default_config: ShowDefaultConfigOpt = False,
) -> None:
    """
    Global option callback. Executed if no command is provided.
    """

    cli_log_level, more_than_one_flag = process_log_flags(
        very_verbose=very_verbose, verbose=verbose, quiet=quiet, very_quiet=very_quiet
    )

    if more_than_one_flag:
        log.warning(
            "More than one log level arguments was provided, the log level with more verbosity will be used."
        )
    # Load settings
    settings = load_settings(explicit_config=config)

    # CLI overrides
    if cli_log_level:
        settings.logging.level = cli_log_level
    if log_file:
        settings.logging.file = log_file

    configure_logging_from_settings(settings=settings)

    # Load settings into global context
    ctx.obj = {"settings": settings}
    log.debug("Ended global callback")
