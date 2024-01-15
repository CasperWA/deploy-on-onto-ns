"""Logging to file."""
from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from uvicorn.logging import DefaultFormatter

if TYPE_CHECKING:  # pragma: no cover
    import logging.handlers


@contextmanager
def disable_logging():
    """Temporarily disable logging.

    Usage:

    ```python
    from deploy_on_onto_ns.logger import disable_logging

    # Do stuff, logging to all handlers.
    # ...
    with disable_logging():
        # Do stuff, without logging to any handlers.
        # ...
    # Do stuff, logging to all handlers now re-enabled.
    # ...
    ```

    """
    try:
        # Disable logging lower than CRITICAL level
        logging.disable(logging.CRITICAL)
        yield
    finally:
        # Re-enable logging to desired levels
        logging.disable(logging.NOTSET)


def initiate_logging() -> None:
    """Initiate logging."""
    # Instantiate LOGGER
    logger = logging.getLogger("deploy_on_onto_ns")
    logger.setLevel(logging.DEBUG)

    # Save a file with all messages (DEBUG level)
    root_dir = Path(__file__).parent.parent.resolve()
    logs_dir = root_dir.joinpath("logs/")
    logs_dir.mkdir(exist_ok=True)

    # Set handlers
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir.joinpath("deploy_on_onto_ns.log"), maxBytes=1000000, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Set formatters
    file_formatter = logging.Formatter(
        "[%(levelname)-8s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
        "%d-%m-%Y %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    console_formatter = DefaultFormatter("%(levelprefix)s [%(name)s] %(message)s")
    console_handler.setFormatter(console_formatter)

    # Finalize LOGGER
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
