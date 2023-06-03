#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the args."""
from __future__ import annotations

import logging
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from watchdog.observers import Observer

from .configs_handling import read_from_configs, write_to_configs
from .constants import CONFIGS_LOCATION
from .event_handling import FileModifiedEventHandler

if TYPE_CHECKING:
    import argparse

    from watchdog.observers.api import BaseObserver

__all__: list[str] = ["handle_config_args", "handle_start_args"]


def resolved_path_from_str(raw_path: str) -> Path:
    """Returns the absolute path given a string of a path."""
    return Path(raw_path.strip()).resolve()


def handle_config_args(args: argparse.Namespace) -> int:
    """Function handling the for ``config`` subcommand."""
    config_handle_logger: logging.Logger = logging.getLogger(
        handle_config_args.__name__,
    )
    config_handle_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()
    try:
        if args.new_config is not None:
            new_config: str = args.new_config.strip()
            config_handle_logger.debug("Splitting %s", new_config)
            new_extension, new_path = new_config.split(",")
            config_handle_logger.debug("Got '%s': '%s'", new_extension, new_path)
            configs[new_extension] = new_path
            config_handle_logger.log(
                70,
                "Updated '%s': '%s' from %s",
                new_extension,
                new_path,
                CONFIGS_LOCATION,
            )

        if args.config_to_be_deleted is not None:
            config_to_be_deleted: str = args.config_to_be_deleted.strip()
            config_handle_logger.debug("Deleting '%s'", config_to_be_deleted)
            del configs[config_to_be_deleted]
            config_handle_logger.log(
                70,
                "Deleted '%s' from '%s'",
                config_to_be_deleted,
                CONFIGS_LOCATION,
            )
    except KeyError:
        config_handle_logger.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        return 1
    except Exception as err:  # pylint: disable=broad-exception-caught
        config_handle_logger.exception("Unexpected %s", err.__class__.__name__)
        return 1

    write_to_configs(configs)
    return 0


def handle_start_args(args: argparse.Namespace) -> int:
    """Function handling the for ``start`` subcommand."""
    start_handle_logger: logging.Logger = logging.getLogger(handle_start_args.__name__)

    tracked_path: Path = args.tracked_path

    start_handle_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    if not configs:
        start_handle_logger.critical(
            "No paths for extensions defined in '%s'",
            CONFIGS_LOCATION,
        )
        return 1

    start_handle_logger.debug("Resolving extension paths")
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(raw_path)
        for extension, raw_path in configs.items()
    }
    start_handle_logger.info("Got extension paths")

    start_handle_logger.debug(
        "Creating FileModifiedEventHandler instance tracking '%s'",
        tracked_path,
    )
    event_handler: FileModifiedEventHandler = FileModifiedEventHandler(
        tracked_path,
        extension_paths,
    )

    start_handle_logger.debug("Creating observer")
    observer: BaseObserver = Observer()
    start_handle_logger.debug("Scheduling observer: %s", observer)
    observer.schedule(event_handler, tracked_path, recursive=True)
    start_handle_logger.debug("Starting observer: %s", observer)
    observer.start()
    start_handle_logger.info("Started observer: '%s'", observer.name)
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        start_handle_logger.debug("User stopped/interrupted program")
    finally:
        if observer.is_alive():
            observer.stop()
            start_handle_logger.info("Stopped observer: %s", observer.name)
        observer.join()
        start_handle_logger.debug("Joined observer: %s", observer)
    return 0
