#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Context manager for settings handling."""
from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from pathlib import Path

__all__: list[str] = ["open_json"]


@contextmanager
def open_json(path_to_json: Path) -> Iterator[dict[str, str]]:
    """Context manager wrapping ``open`` for easy access to the json file with exception handling."""
    json_logger: logging.Logger = logging.getLogger(open_json.__name__)
    try:
        json_logger.debug("Opening %s", path_to_json)
        with open(path_to_json, "r", encoding="utf-8") as settings:
            json_logger.debug("Loading and yielding %s", settings)
            yield json.load(settings)
        json_logger.info("Yielded %s", settings)
    except FileNotFoundError as no_file_exce:
        json_logger.critical(
            "Unable to find json file %s",
            path_to_json,
        )
        raise SystemExit(1) from no_file_exce
    except KeyError as key_exce:
        json_logger.critical(
            "Given json file is not correctly configured: %s",
            path_to_json,
        )
        raise SystemExit(1) from key_exce
    except json.JSONDecodeError as json_decode_exce:
        json_logger.critical(
            "Given json file is not correctly formatted: %s",
            path_to_json,
        )
        raise SystemExit(1) from json_decode_exce
    except Exception as exce:  # pylint: disable=broad-exception-caught
        json_logger.exception("Unexpected %s", exce.__class__.__name__)
        raise SystemExit(1) from exce
