#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the JSON configs."""
from __future__ import annotations

import json
import logging

from .constants import CONFIGS_LOCATION

__all__: list[str] = ["read_from_configs", "write_to_configs"]


# pylint: disable=broad-exception-caught


def read_from_configs() -> dict[str, str]:
    """Function wrapping ``open`` for reading from ``configs.json`` with exception handling and logging."""
    reading_logger: logging.Logger = logging.getLogger(read_from_configs.__name__)
    try:
        reading_logger.debug("Opening %s", CONFIGS_LOCATION)
        with open(CONFIGS_LOCATION, "r", encoding="utf-8") as json_file:
            reading_logger.debug("Loading %s", json_file)
            config_dict: dict[str, str] = json.load(json_file)
        reading_logger.log(70, "Read from %s", CONFIGS_LOCATION)
    except FileNotFoundError as no_file_err:
        reading_logger.info(
            "Unable to find 'configs.json', falling back to an empty configuration",
        )
        config_dict = {}
        write_to_configs(config_dict)
        raise SystemExit(1) from no_file_err
    except json.JSONDecodeError as json_decode_err:
        reading_logger.critical(
            "Given JSON file is not correctly formatted: %s",
            CONFIGS_LOCATION,
        )
        raise SystemExit(1) from json_decode_err
    except Exception as err:
        reading_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(1) from err
    return config_dict


def write_to_configs(new_configs: dict[str, str]) -> None:
    """Function wrapping ``open`` for writing to ``configs.json`` with exception handling and logging."""
    writing_logger: logging.Logger = logging.getLogger(write_to_configs.__name__)
    try:
        writing_logger.debug("Opening 'extension.json'")
        with open(CONFIGS_LOCATION, "w", encoding="utf-8") as json_file:
            writing_logger.debug("Dumping: %s", new_configs)
            json.dump(new_configs, json_file, indent=4)
        writing_logger.log(
            70,
            "Added new extension configuration: %s",
            new_configs,
        )
    except KeyError as key_err:
        writing_logger.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        raise SystemExit(1) from key_err
    except Exception as err:
        writing_logger.exception("Unexpected %s", err.__class__.__name__)
        raise SystemExit(1) from err
