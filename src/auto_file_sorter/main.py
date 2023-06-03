#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import argparse
import logging
from typing import Optional, Sequence, TextIO

from . import __version__
from .args_handling import handle_config_args, handle_start_args, resolved_path_from_str
from .constants import LOG_FORMAT, LOG_LOCATION

__all__: list[str] = ["main"]

_verbose_output_levels: dict[int, int] = {
    1: logging.ERROR,
    2: logging.INFO,
    3: logging.DEBUG,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Runs the program."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="auto-file-sorter")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{parser.prog} {__version__}",
        help="Show version of auto-file-sorter",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debugging",
        help="Enable debugging by setting logging level to 10",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Show output",
    )

    subparsers: argparse._SubParsersAction[  # noqa: SLF001
        argparse.ArgumentParser
    ] = parser.add_subparsers(title="subcommands", required=True)

    # "start" subcommand
    start_parser: argparse.ArgumentParser = subparsers.add_parser(
        "start",
        help="Start the automation",
    )
    start_parser.set_defaults(handle=handle_start_args)
    start_parser.add_argument(
        type=resolved_path_from_str,
        dest="tracked_path",
        help="Set path to be tracked",
    )

    # "config" subcommand
    config_parser: argparse.ArgumentParser = subparsers.add_parser(
        "config",
        help="Configure the program",
    )
    config_parser.set_defaults(
        handle=handle_config_args,
    )
    config_parser.add_argument(
        "-A",
        "--add",
        dest="new_config",
        type=str,
        help="Add path for extension",
    )
    config_parser.add_argument(
        "-D",
        "--delete",
        dest="config_to_be_deleted",
        type=str,
        help="Add path for extension",
    )

    args: argparse.Namespace = parser.parse_args(argv)

    # custom "MOVEMENT" and "CONFIGURATION" logging level >= logging.CRITICAL (50)
    # so it can be handeled by the stream handler if verbose logging is enabled
    logging.addLevelName(60, "MOVEMENT")
    logging.addLevelName(70, "CONFIGURATION")

    file_handler: logging.FileHandler = logging.FileHandler(
        filename=LOG_LOCATION,
        mode="w",
        encoding="utf-8",
    )

    handlers: list[logging.Handler] = [file_handler]

    if 1 <= args.verbose <= 3:  # noqa: PLR2004
        stream_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        stream_handler.setLevel(_verbose_output_levels[args.verbose])
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        handlers.append(stream_handler)

    log_level: int = logging.INFO if not args.debugging else logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers,
    )

    main_logger: logging.Logger = logging.getLogger(main.__name__)
    main_logger.debug("Got %s", args)
    main_logger.info(
        "Started logging with level %s",
        log_level,
    )

    return args.handle(args)


if __name__ == "__main__":
    raise SystemExit(main())
