#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Context manager for settings handling."""
from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Iterator, TypeAlias

import PySimpleGUI as sg

__all__: list[str] = ["open_settings", "Settings"]

Settings: TypeAlias = dict[str, dict[str, int | str]]


@contextmanager
def open_settings(path_to_settings: str) -> Iterator[Settings]:
    """Wrapper Function that creates context manager for easy access to the settings json file with exception handling.

    :rtype: Iterator[dict[str, dict[str, int | str]]]
    """
    try:
        with open(path_to_settings, "r", encoding="utf-8") as settings:
            yield json.load(settings)
    except FileNotFoundError as no_file_exce:
        sg.PopupError(
            f"{__file__}:\nSettings json file not found. Must be located in the same directory as the executable.",
            title="auto-file-sorter",
        )
        raise SystemExit(1) from no_file_exce
    except KeyError as key_exce:
        sg.PopupError(
            f"{__file__}:\nSettings json file is not correctly configured.",
            title="auto-file-sorter",
        )
        raise SystemExit(1) from key_exce
    except json.JSONDecodeError as json_decode_exce:
        sg.PopupError(
            f"{__file__}:\nSettings json file is not correctly formatted.",
            title="auto-file-sorter",
        )
        raise SystemExit(1) from json_decode_exce
    except Exception as exce:  # pylint: disable=broad-exception-caught
        sg.PopupError(
            f"Unexpected {exce.__class__.__name__}",
        )
        raise SystemExit(1) from exce
