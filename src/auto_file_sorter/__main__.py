#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run module as file."""
from __future__ import annotations

from .main import main

__all__: list[str] = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
