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

from auto_file_sorter.configs_handling import read_from_configs, write_to_configs
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    CONFIGS_LOCATION,
    EXIT_FAILURE,
    EXIT_SUCCESS,
)
from auto_file_sorter.event_handling import OnModifiedEventHandler

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

            new_extension, new_path = (
                args.new_config[0].strip(),
                args.new_config[1].strip(),
            )

            if not new_extension or not new_path:
                config_handle_logger.critical(
                    "No extension ('%s') or path ('%s') were given to be added",
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

        if args.get_configs is not None:
            config_handle_logger.debug(
                "get_configs=%s",
                repr(args.get_configs),
            )

            config_handle_logger.debug(
                "Getting selected configs and storing them in dict",
            )
            selected_configs: dict[str, Path] = {
                config: resolved_path_from_str(configs[config])
                for config in args.get_configs
            }

            config_handle_logger.log(
                CONFIG_LOG_LEVEL,
                "Printing from %s",
                selected_configs,
            )

            for extension, path in selected_configs.items():
                print(f"{extension}: {path}")
            return EXIT_SUCCESS

        if args.get_all_configs is not None:
            for extension, raw_path in configs.items():
                print(f"{extension}: {resolved_path_from_str(raw_path)}")
            return EXIT_SUCCESS

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

    tracked_paths: list[Path] = args.tracked_paths
    track_handle_logger.debug("tracked_paths=%s", tracked_paths)

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

    observers: list[BaseObserver] = []
    for path in tracked_paths:
        track_handle_logger.debug(
            "Creating FileModifiedEventHandler instance tracking '%s'",
            path,
        )
        event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
            path,
            extension_paths,
        )

        track_handle_logger.debug("Creating observer")
        observer: BaseObserver = Observer()
        track_handle_logger.debug("Scheduling observer: %s", observer)
        observer.schedule(event_handler, path, recursive=True)
        track_handle_logger.debug("Starting observer: %s", observer)
        observer.start()
        track_handle_logger.info("Started observer: '%s'", observer.name)
        observers.append(observer)
        track_handle_logger.debug("Appended '%s' to %s", observer, observers)

    track_handle_logger.debug("observers=%s", observers)

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        track_handle_logger.debug("User stopped/interrupted program")
    finally:
        for observer in observers:
            if observer.is_alive():
                observer.stop()
                track_handle_logger.info("Stopped observer: %s", observer.name)
            observer.join()
            track_handle_logger.debug("Joined observer: %s", observer)
    return EXIT_SUCCESS
