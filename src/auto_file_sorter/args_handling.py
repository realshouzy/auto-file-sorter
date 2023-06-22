#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the args."""
from __future__ import annotations

__all__: list[str] = ["handle_config_args", "handle_track_args"]

import logging
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Literal

from watchdog.observers import Observer

from auto_file_sorter.configs_handling import (
    read_from_configs,
    write_to_configs,
)
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    CONFIGS_LOCATION,
    EXIT_FAILURE,
    EXIT_SUCCESS,
)
from auto_file_sorter.event_handling import FileModifiedEventHandler

if TYPE_CHECKING:
    import argparse

    from watchdog.observers.api import BaseObserver


def resolved_path_from_str(raw_path: str) -> Path:
    """Returns the absolute path given a string of a path."""
    return Path(raw_path).resolve()


def handle_config_args(args: argparse.Namespace) -> Literal[0, 1]:
    """Function handling the for ``config`` subcommand."""
    config_handle_logger: logging.Logger = logging.getLogger(
        handle_config_args.__name__,
    )
    config_handle_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    try:
        if args.new_config is not None:
            config_handle_logger.debug("new_config=%s", repr(args.new_config))

            new_raw_extension, new_raw_path = args.new_config

            new_extension, new_path = (
                new_raw_extension.strip(),
                new_raw_path.strip(),
            )

            if not new_extension or not new_path:
                config_handle_logger.critical(
                    "No extension ('%s') or path ('%s')",
                    new_extension,
                    new_path,
                )
                return EXIT_FAILURE

            if not new_extension.startswith("."):
                new_extension: str = f".{new_extension}"

            new_path = str(resolved_path_from_str(new_path))

            config_handle_logger.debug(
                "Got '%s': '%s'",
                new_extension,
                new_path,
            )
            configs[new_extension] = new_path
            config_handle_logger.log(
                CONFIG_LOG_LEVEL,
                "Updated '%s': '%s' from %s",
                new_extension,
                new_path,
                CONFIGS_LOCATION,
            )

        if args.configs_to_be_deleted is not None:
            config_handle_logger.debug(
                "configs_to_be_deleted=%s",
                repr(args.configs_to_be_deleted),
            )

            for config in args.configs_to_be_deleted:
                config_handle_logger.debug("Normalizing '%s'", config)
                extension: str = config.strip()
                config_handle_logger.debug("Stripped '%s", extension)

                if not extension.startswith("."):
                    extension: str = f".{extension}"

                config_handle_logger.debug(
                    "Normalized '%s' to '%s'",
                    config,
                    extension,
                )

                # skip if the extension is not in the configs or the user provided an empty string
                if extension not in configs.keys() or extension == ".":
                    config_handle_logger.debug("Skipping '%s'", extension)
                    continue

                config_handle_logger.debug("Deleting '%s'", extension)
                del configs[extension]
                config_handle_logger.log(
                    CONFIG_LOG_LEVEL,
                    "Deleted '%s'",
                    extension,
                )
    except KeyError:
        config_handle_logger.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        return EXIT_FAILURE
    except Exception as err:
        config_handle_logger.exception("Unexpected %s", err.__class__.__name__)
        return EXIT_FAILURE

    write_to_configs(configs)
    return EXIT_SUCCESS


def handle_track_args(args: argparse.Namespace) -> Literal[0, 1]:
    """Function handling the for ``start`` subcommand."""
    track_handle_logger: logging.Logger = logging.getLogger(
        handle_track_args.__name__,
    )

    tracked_path: Path = args.tracked_path

    track_handle_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    if not configs:
        track_handle_logger.critical(
            "No paths for extensions defined in '%s'",
            CONFIGS_LOCATION,
        )
        return EXIT_FAILURE

    track_handle_logger.debug("Resolving extension paths")
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(raw_path)
        for extension, raw_path in configs.items()
    }
    track_handle_logger.info("Got extension paths")

    track_handle_logger.debug(
        "Creating FileModifiedEventHandler instance tracking '%s'",
        tracked_path,
    )
    event_handler: FileModifiedEventHandler = FileModifiedEventHandler(
        tracked_path,
        extension_paths,
    )

    track_handle_logger.debug("Creating observer")
    observer: BaseObserver = Observer()
    track_handle_logger.debug("Scheduling observer: %s", observer)
    observer.schedule(event_handler, tracked_path, recursive=True)
    track_handle_logger.debug("Starting observer: %s", observer)
    observer.start()
    track_handle_logger.info("Started observer: '%s'", observer.name)

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        track_handle_logger.debug("User stopped/interrupted program")
    finally:
        if observer.is_alive():
            observer.stop()
            track_handle_logger.info("Stopped observer: %s", observer.name)
        observer.join()
        track_handle_logger.debug("Joined observer: %s", observer)
    return EXIT_SUCCESS
