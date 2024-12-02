"""Module defining and containing global constants."""

from __future__ import annotations

__all__: list[str] = [
    "CONFIG_LOG_LEVEL",
    "DEFAULT_CONFIGS_LOCATION",
    "DEFAULT_LOG_LOCATION",
    "EXIT_FAILURE",
    "EXIT_SUCCESS",
    "FILE_EXTENSION_PATTERN",
    "LOG_FORMAT",
    "MAX_VERBOSITY_LEVEL",
    "MOVE_LOG_LEVEL",
    "PROGRAM_LOCATION",
    "STREAM_HANDLER_FORMATTER",
]

import logging
import re
from pathlib import Path
from typing import Final

PROGRAM_LOCATION: Final[Path] = Path(__file__).resolve().parent
DEFAULT_CONFIGS_LOCATION: Final[Path] = PROGRAM_LOCATION / "configs.json"
DEFAULT_LOG_LOCATION: Final[Path] = PROGRAM_LOCATION / "auto-file-sorter.log"

LOG_FORMAT: Final = "%(name)s [%(levelname)s] %(asctime)s - %(message)s"
MOVE_LOG_LEVEL: Final = 60
CONFIG_LOG_LEVEL: Final = 70
STREAM_HANDLER_FORMATTER: Final[logging.Formatter] = logging.Formatter(
    "[%(levelname)s] %(message)s",
)

VERBOSE_OUTPUT_LEVELS: Final[dict[int, int]] = {
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}
MAX_VERBOSITY_LEVEL: Final = 3

FILE_EXTENSION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^\.[a-zA-Z0-9]+$",
    re.IGNORECASE,
)

EXIT_SUCCESS: Final = 0
EXIT_FAILURE: Final = 1
