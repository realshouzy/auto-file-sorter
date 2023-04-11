# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Context manager for settings handling."""
from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from typing import Iterator, TypeAlias

import PySimpleGUI as sg

__all__: list[str] = ["open_settings", "Settings"]

Settings: TypeAlias = dict[str, dict[str, int | str]]


@contextmanager
def open_settings() -> Iterator[Settings]:
    """Wrapper Function that creates context manager for easy access to the settings json file with exception handling.

    :rtype: Iterator[dict[str, dict[str, int | str]]]
    """
    try:
        with open("settings.json", "r", encoding="utf-8") as settings:
            yield json.load(settings)
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
    except json.JSONDecodeError:
        sg.PopupError(
            f"{__file__}:\nSettings json file is not correctly formatted.",
            title="FileSorter",
        )
        sys.exit(1)
    except Exception as exce:  # pylint: disable=broad-exception-caught
        sg.PopupError(
            f"Unexpected {exce.__class__.__name__}",
        )
