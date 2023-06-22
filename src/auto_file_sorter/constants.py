#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module defining and containing global constants."""
from __future__ import annotations

__all__: list[str] = [
    "PROGRAM_LOCATION",
    "CONFIGS_LOCATION",
    "DEFAULT_LOG_LOCATION",
    "LOG_FORMAT",
    "MOVE_LOG_LEVEL",
    "CONFIG_LOG_LEVEL",
    "STREAM_HANDLER_FORMATTER",
    "MAX_VERBOSITY_LEVEL",
    "EXIT_SUCCESS",
    "EXIT_FAILURE",
]

import logging
from pathlib import Path
from typing import Final, Literal

PROGRAM_LOCATION: Final[Path] = Path(__file__).resolve().parent
CONFIGS_LOCATION: Final[Path] = PROGRAM_LOCATION.joinpath("configs.json")
DEFAULT_LOG_LOCATION: Final[Path] = PROGRAM_LOCATION.joinpath(
    "auto-file-sorter.log",
)

LOG_FORMAT: Final[
    Literal["%(name)s [%(levelname)s] %(asctime)s - %(message)s"]
] = "%(name)s [%(levelname)s] %(asctime)s - %(message)s"
MOVE_LOG_LEVEL: Final[Literal[60]] = 60
CONFIG_LOG_LEVEL: Final[Literal[70]] = 70
STREAM_HANDLER_FORMATTER: Final[logging.Formatter] = logging.Formatter(
    "[%(levelname)s] %(message)s",
)
MAX_VERBOSITY_LEVEL: Final[Literal[3]] = 3

EXIT_SUCCESS: Final[Literal[0]] = 0
EXIT_FAILURE: Final[Literal[1]] = 1