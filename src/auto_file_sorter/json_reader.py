#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""JSON reader."""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

__all__: list[str] = ["read_from_json"]


def read_from_json(path_to_json: Path) -> dict[str, str]:
    """Function wrapping ``open`` for easy access to the JSON file with exception handling and logging."""
    json_logger: logging.Logger = logging.getLogger(read_from_json.__name__)
    try:
        json_logger.debug("Opening %s", path_to_json)
        with open(path_to_json, "r", encoding="utf-8") as json_content:
            json_logger.debug("Loading %s", json_content)
            extension_dict: dict[str, str] = json.load(json_content)
        json_logger.info("Read from %s", path_to_json)
    except FileNotFoundError as no_file_err:
        json_logger.critical(
            "Unable to find JSON file %s",
            path_to_json,
        )
        raise SystemExit(1) from no_file_err
    except KeyError as key_err:
        json_logger.critical(
            "Given JSON file is not correctly configured: %s",
            path_to_json,
        )
        raise SystemExit(1) from key_err
    except json.JSONDecodeError as json_decode_err:
        json_logger.critical(
            "Given JSON file is not correctly formatted: %s",
            path_to_json,
        )
        raise SystemExit(1) from json_decode_err
    except Exception as err:  # pylint: disable=broad-exception-caught
        json_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(1) from err
    return extension_dict
