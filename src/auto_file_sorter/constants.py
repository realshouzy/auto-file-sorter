#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module defining and containing global constants."""
from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

__all__: list[str] = [
    "PROGRAM_LOCATION",
    "CONFIGS_LOCATION",
    "LOG_LOCATION",
    "LOG_FORMAT",
    "MAX_VERBOSITY_LEVEL",
]

PROGRAM_LOCATION: Final[Path] = Path(__file__).resolve().parent
CONFIGS_LOCATION: Final[Path] = PROGRAM_LOCATION.joinpath("configs.json")
LOG_LOCATION: Final[Path] = PROGRAM_LOCATION.joinpath("auto-file-sorter.log")

LOG_FORMAT: Final[str] = "%(name)s [%(levelname)s] %(asctime)s - %(message)s"
MAX_VERBOSITY_LEVEL: Final[Literal[3]] = 3
