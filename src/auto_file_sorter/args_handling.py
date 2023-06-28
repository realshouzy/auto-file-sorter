#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the args."""
from __future__ import annotations

__all__: list[str] = ["handle_write_args", "handle_read_args", "handle_track_args"]

import json
import logging
import os
import platform
import sys
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


def _add_to_startup() -> None:
    """Add the ran command to startup by creating a vbs file in the 'Startup' folder."""
    add_to_startup_logger: logging.Logger = logging.getLogger(_add_to_startup.__name__)
    if platform.system() != "Windows":
        add_to_startup_logger.warning(
            "Adding 'auto-file-sorter' to startup is only supported on Windows.",
        )
        return

    add_to_startup_logger.debug("sys.argv=%s", sys.argv)

    flags_to_be_removed: list[str] = [
        "-v",
        "-vv",
        "-vvv",
        "--verbose",
        "-A",
        "--autostart",
    ]

    cleaned_sys_argv: list[str] = [
        arg for arg in sys.argv if arg not in flags_to_be_removed
    ]
    cmd: str = " ".join(cleaned_sys_argv)
    add_to_startup_logger.debug("Adding '%s' to autostart", cmd)

    startup_folder: Path = Path(os.path.expandvars("%APPDATA%")).joinpath(
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )
    add_to_startup_logger.debug("Startup folder location: '%s'", startup_folder)
    path_to_vbs: Path = startup_folder.joinpath("auto-file-sorter.vbs")

    add_to_startup_logger.debug("Opening vbs file: '%s'", path_to_vbs)
    with open(path_to_vbs, "w", encoding="utf-8") as vbs_file:
        add_to_startup_logger.debug("Writing to vsb file: '%s'", vbs_file)
        vbs_file.write(
            f'Set objShell = WScript.CreateObject("WScript.Shell")\nobjShell.Run "{cmd}", 0, True',
        )
    add_to_startup_logger.info(
        "Added '%s' with '%s' to startup",
        path_to_vbs,
        cmd,
    )


def resolved_path_from_str(path_as_str: str) -> Path:
    """Returns the absolute path given a string of a path."""
    return Path(path_as_str).resolve()


def handle_write_args(args: argparse.Namespace) -> Literal[0, 1]:
    """Function handling the ``write`` subcommand."""
    write_handle_logger: logging.Logger = logging.getLogger(
        handle_write_args.__name__,
    )

    write_handle_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    try:
        if args.new_config is not None:
            write_handle_logger.debug("args.new_config=%s", repr(args.new_config))

            new_extension, new_path = (
                args.new_config[0].strip(),
                args.new_config[1].strip(),
            )

            if not new_extension or not new_path:
                write_handle_logger.critical(
                    "No extension ('%s') or path ('%s') were given to be added",
                    new_extension,
                    new_path,
                )
                return EXIT_FAILURE

            if not new_extension.startswith("."):
                new_extension: str = f".{new_extension.lower()}"

            write_handle_logger.debug("Got '%s': '%s'", new_extension, new_path)

            configs[new_extension] = new_path
            write_handle_logger.log(
                CONFIG_LOG_LEVEL,
                "Updated '%s': '%s' from %s",
                new_extension,
                new_path,
                CONFIGS_LOCATION,
            )

        if args.new_configs_file is not None:
            write_handle_logger.debug(
                "args.new_configs_file='%s'",
                repr(args.new_configs_file),
            )

            if args.new_configs_file.suffix.lower() != ".json":
                write_handle_logger.critical(
                    "Configs can only be read from json files",
                )
                return EXIT_FAILURE

            write_handle_logger.debug("Opening '%s'", args.new_configs_file)
            with open(args.new_configs_file, "r", encoding="utf-8") as json_file:
                write_handle_logger.debug("Reading from '%s'", args.new_configs_file)
                new_configs_from_json: dict[str, str] = json.load(json_file)
            write_handle_logger.debug("Read from '%s'", args.new_configs_file)

            configs |= new_configs_from_json
            write_handle_logger.log(
                CONFIG_LOG_LEVEL,
                "Loaded '%s' into configs",
                args.new_configs_file,
            )

        if args.configs_to_be_deleted is not None:
            write_handle_logger.debug(
                "args.configs_to_be_deleted=%s",
                repr(args.configs_to_be_deleted),
            )

            for config in args.configs_to_be_deleted:
                write_handle_logger.debug("Normalizing '%s'", config)
                extension: str = config.strip()
                write_handle_logger.debug("Stripped '%s", extension)

                if not extension.startswith("."):
                    extension: str = f".{extension.lower()}"

                write_handle_logger.debug("Normalized '%s' to '%s'", config, extension)

                # Skip if the extension is not in the configs or the user provided an empty string
                if extension not in configs.keys() or extension == ".":
                    write_handle_logger.debug("Skipping '%s'", extension)
                    continue

                write_handle_logger.debug("Deleting '%s'", extension)
                del configs[extension]
                write_handle_logger.log(
                    CONFIG_LOG_LEVEL,
                    "Deleted '%s'",
                    extension,
                )

    except KeyError:
        write_handle_logger.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        return EXIT_FAILURE
    except FileNotFoundError:
        write_handle_logger.critical(
            "Unable to find '%s'",
            args.new_configs_file,
        )
        return EXIT_FAILURE
    except json.JSONDecodeError:
        write_handle_logger.critical(
            "Given JSON file is not correctly formatted: %s",
            args.new_configs_file,
        )
        return EXIT_FAILURE
    except Exception as err:
        write_handle_logger.exception("Unexpected %s", err.__class__.__name__)
        return EXIT_FAILURE

    write_to_configs(configs)
    return EXIT_SUCCESS


def handle_read_args(args: argparse.Namespace) -> Literal[0, 1]:
    """Function handling the ``read`` subcommand."""
    read_handle_logger: logging.Logger = logging.getLogger(handle_read_args.__name__)

    read_handle_logger.debug("Reading from configs")
    configs: dict[str, str] = read_from_configs()

    try:
        if not args.get_configs:
            for extension, raw_path in configs.items():
                print(f"{extension}: {resolved_path_from_str(raw_path)}")
            read_handle_logger.log(
                CONFIG_LOG_LEVEL,
                "Printed all the configs",
            )
        else:
            read_handle_logger.debug("args.get_configs=%s", repr(args.get_configs))

            read_handle_logger.debug(
                "Getting selected configs and storing them in dict",
            )
            selected_configs: dict[str, Path] = {
                config: resolved_path_from_str(configs[config])
                for config in args.get_configs
            }

            read_handle_logger.debug("Printing from %s", selected_configs)
            for extension, path in selected_configs.items():
                print(f"{extension}: {path}")
            read_handle_logger.log(
                CONFIG_LOG_LEVEL,
                "Printed the selected configs",
            )
    except KeyError:
        read_handle_logger.critical(
            "Given JSON file is not correctly configured: %s",
            CONFIGS_LOCATION,
        )
        return EXIT_FAILURE
    except Exception as err:
        read_handle_logger.exception("Unexpected %s", err.__class__.__name__)
        return EXIT_FAILURE

    return EXIT_SUCCESS


def handle_track_args(args: argparse.Namespace) -> Literal[0, 1]:
    """Function handling the ``start`` subcommand."""
    track_handle_logger: logging.Logger = logging.getLogger(
        handle_track_args.__name__,
    )

    if args.enable_autostart:
        _add_to_startup()

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
