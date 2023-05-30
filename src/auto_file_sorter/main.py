#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import argparse
from typing import Optional, Sequence

from . import __version__
from .args_handling import handle_config, handle_start, resolved_path_from_str

__all__: list[str] = ["main"]


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

    subparsers: argparse._SubParsersAction[  # noqa: SLF001
        argparse.ArgumentParser
    ] = parser.add_subparsers(title="subcommands", required=True)

    # "start" subcommand
    start_parser: argparse.ArgumentParser = subparsers.add_parser(
        "start",
        help="Start the automation",
    )
    start_parser.set_defaults(handle=handle_start)
    start_parser.add_argument(
        "-p",
        "--path",
        type=resolved_path_from_str,
        dest="tracked_path",
        help="Set path to be tracked",
        required=True,
    )
    start_parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debugging",
        help="Enable debugging by setting logging level to 10",
    )
    start_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Show output",
    )

    # "config" subcommand
    config_parser: argparse.ArgumentParser = subparsers.add_parser(
        "config",
        help="Configure the program",
    )
    config_parser.set_defaults(
        handle=handle_config,
    )
    config_parser.add_argument(
        "-f",
        "--format",
        dest="format",
        type=str,
        help="Set logging format",
    )
    config_parser.add_argument(
        "-rf",
        "--reset-format",
        action="store_const",
        const="%(name)s %(levelname)s %(asctime)s - %(message)s",
        dest="format",
        help="Reset the logging level to default",
    )
    config_parser.add_argument(
        "-l",
        "--level",
        type=int,
        dest="level",
        help="Set logging level",
    )
    config_parser.add_argument(
        "-rl",
        "--reset-level",
        action="store_const",
        const=20,
        dest="level",
        help="Reset the logging level to default",
    )
    config_parser.add_argument(
        "-a",
        "--add",
        dest="new_extension_path",
        type=str,
        help="Add path for extension",
    )
    config_parser.add_argument(
        "-d",
        "--delete",
        dest="extension_path_to_be_deleted",
        type=str,
        help="Add path for extension",
    )

    args: argparse.Namespace = parser.parse_args(argv)
    args.handle(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
