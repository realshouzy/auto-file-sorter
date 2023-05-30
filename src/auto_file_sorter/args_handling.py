#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module responsible for handling the args."""
from __future__ import annotations

import logging
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, TextIO

from watchdog.observers import Observer

from .configs_handling import (
    PROGRAM_LOCATION,
    Configs,
    read_from_configs,
    write_to_configs,
)
from .event_handling import FileModifiedEventHandler

if TYPE_CHECKING:
    import argparse

    from watchdog.observers.api import BaseObserver

__all__: list[str] = ["handle_config", "handle_start", "resolved_path_from_str"]

_verbose_output_levels: dict[int, int] = {
    1: logging.ERROR,
    2: logging.INFO,
    3: logging.DEBUG,
}


def resolved_path_from_str(raw_path: str) -> Path:
    """Returns the absolute path given a string of a path."""
    return Path(raw_path).resolve()


def handle_config(args: argparse.Namespace) -> None:
    """Function handling the for ``config`` subcommand."""
    old_configs: Configs = read_from_configs()

    level: int = old_configs.level if args.level is None else args.level
    format_: str = old_configs.format if args.format is None else args.format
    extension_paths: dict[str, str] = old_configs.extension_paths
    if args.new_extension_path is not None:
        new_extension, new_path = args.new_extension_path.split(",")
        extension_paths[new_extension] = new_path

    if args.extension_path_to_be_deleted is not None:
        del extension_paths[args.extension_path_to_be_deleted]

    new_configs: Configs = Configs(level, format_, extension_paths)
    write_to_configs(new_configs)


def handle_start(args: argparse.Namespace) -> None:
    """Function handling the for ``start`` subcommand."""
    # custom "MOVE" logging level >= logging.CRITICAL (50)
    # so it can be handeled by the stream handler if verbose logging is enabled
    configs: Configs = read_from_configs()

    logging.addLevelName(60, "MOVE")

    file_handler: logging.FileHandler = logging.FileHandler(
        filename=PROGRAM_LOCATION.joinpath("auto-file-sorter.log"),
        mode="w",
        encoding="utf-8",
    )

    handlers: list[logging.Handler] = [file_handler]

    if args.verbose:
        stream_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        stream_handler.setLevel(_verbose_output_levels[args.verbose])
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        handlers.append(stream_handler)

    logging.basicConfig(
        level=configs.level,
        format=configs.format,
        handlers=handlers,
    )

    main_logger: logging.Logger = logging.getLogger(handle_config.__name__)
    main_logger.debug("Got %s", args)
    main_logger.info(
        "Started logging with format '%s' and level %s",
        configs.format,
        configs.level,
    )
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(raw_path)
        for extension, raw_path in configs.extension_paths.items()
    }
    main_logger.info("Got extension paths")

    event_handler: FileModifiedEventHandler = FileModifiedEventHandler(
        args.tracked_path,
        extension_paths,
    )

    main_logger.debug("Creating observer")
    observer: BaseObserver = Observer()
    main_logger.debug("Scheduling observer: %s", observer)
    observer.schedule(event_handler, args.tracked_path, recursive=True)
    main_logger.debug("Starting observer: %s", observer)
    observer.start()
    main_logger.info("Started observer: '%s'", observer.name)
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        main_logger.debug("User stopped/interrupted program")
    finally:
        if observer.is_alive():
            observer.stop()
            main_logger.info("Stopped observer: %s", observer.name)
        observer.join()
        main_logger.debug("Joined observer: %s", observer)
