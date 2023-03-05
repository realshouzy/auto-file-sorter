# -*- coding: UTF-8 -*-
"""Context manager for settings handling."""
from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, NoReturn, TypeAlias

import PySimpleGUI as sg

Settings: TypeAlias = dict[str, dict[str, Path | int | str]]


@contextmanager
def open_settings() -> Iterator[Settings] | NoReturn:
    """Wrapper Function that creates context manager for easy access to the settings json file with exception handling.

    :rtype: Iterator[dict[str, dict[str, Path | int | str]]]
    """
    try:
        with open("settings.json", "r", encoding="UTF-8") as f:
            yield json.load(f)
    except FileNotFoundError:
        sg.PopupError(
            f"{__file__}:\nSettings json file not found. Must be located in the same directory as the executable.",
            title="FileSorter",
        )
        sys.exit(1)
    except KeyError:
        sg.PopupError(
            f"{__file__}:\nSettings json file is not correctly configured.",
            title="FileSorter",
        )
        sys.exit(1)
    # except Exception as exce:
    #     sg.PopupError(
    #         f"Unexpected {exce.__class__.__name__} -> check log for more info.",
    #     )
