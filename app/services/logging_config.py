
import logging
import os
from pathlib import Path


def configure_logging() -> None:
    """Log application events to the console and results/error.log."""
    log_dir = Path("results")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "error.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if configuration is called twice.
    if any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == log_file.resolve()
        for handler in root_logger.handlers
    ):
        return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
