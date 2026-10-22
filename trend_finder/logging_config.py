"""Daily rotating Loguru configuration."""

import logging
import sys
from pathlib import Path

from loguru import logger


class InterceptHandler(logging.Handler):
    """Forward standard-library logs, including aiogram logs, to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Pass a standard logging record to the matching Loguru level."""
        level: str | int = record.levelno
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            pass
        logger.opt(exception=record.exc_info, depth=6).log(level, record.getMessage())


def configure_logging(log_dir: str, log_level: str) -> None:
    """Configure console logging and a daily rotating application log."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stderr, level=log_level.upper(), backtrace=False, diagnose=False)
    logger.add(
        str(Path(log_dir) / "trend-finder-{time:YYYY-MM-DD}.log"),
        level=log_level.upper(),
        rotation="00:00",
        retention="14 days",
        encoding="utf-8",
        backtrace=False,
        diagnose=False,
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
