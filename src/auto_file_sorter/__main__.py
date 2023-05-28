#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Optional, Sequence

from watchdog.observers import Observer

from . import __version__
from .event_handler import FileModifiedEventHandler
from .json_reader import read_from_json

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver

__all__: list[str] = ["main"]


def _resolved_path_from_str(raw_path: str) -> Path:
    """Returns the absolute path given a string of a path."""
    return Path(raw_path).resolve()


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Runs the program."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"auto-file-sorter {__version__}",
        help="version of auto-file-sorter",
    )

    # "run" subcommand
    subparsers: argparse._SubParsersAction[  # noqa: SLF001
        argparse.ArgumentParser
    ] = parser.add_subparsers(title="subcommands", required=True)

    start_parser: argparse.ArgumentParser = subparsers.add_parser(
        "start",
        aliases=["run"],
        help="start the automation",
    )

    start_parser.add_argument(
        "-p",
        "--path",
        "--tracked-path",
        type=_resolved_path_from_str,
        help="sets path to be tracked",
        required=True,
    )
    start_parser.add_argument(
        "-e",
        "--extensions",
        "--extension-paths",
        type=_resolved_path_from_str,
        help="set path to JSON file",
        required=True,
    )
    start_parser.add_argument(
        "-lf",
        "--log-format",
        "--logging-format",
        default=r"%(name)s %(levelname)s %(asctime)s - %(message)s",
        type=str,
        help="set logging format",
    )
    start_parser.add_argument(
        "-ll",
        "--log-level",
        "--logging-level",
        default=logging.INFO,  # 20
        type=int,
        help="set logging level",
    )
    start_parser.add_argument(
        "-d",
        "--debug",
        "--debugging",
        action="store_const",
        const=logging.DEBUG,  # 10
        dest="log_level",
        help="set logging level to debugging (10)",
    )
    # TODO: Add ``auto-start`` sub command for adding the automation to the startups folder

    args: argparse.Namespace = parser.parse_args(argv)

    logging.basicConfig(
        filename="auto-file-sorter.log",
        level=args.log_level,
        format=args.log_format,
        filemode="w",
    )
    main_logger: logging.Logger = logging.getLogger(main.__name__)
    main_logger.debug("Got %s", args)
    main_logger.info(
        "Started logging with format '%s' and level %s",
        args.log_format,
        args.log_level,
    )

    extension_paths: dict[str, Path] = {
        extension: _resolved_path_from_str(raw_path)
        for extension, raw_path in read_from_json(args.extensions).items()
    }
    main_logger.info("Got extension paths from %s", args.extensions)

    event_handler: FileModifiedEventHandler = FileModifiedEventHandler(
        args.path,
        extension_paths,
    )

    main_logger.debug("Creating observer")
    observer: BaseObserver = Observer()
    main_logger.debug("Scheduling observer: %s", observer)
    observer.schedule(event_handler, args.path, recursive=True)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())