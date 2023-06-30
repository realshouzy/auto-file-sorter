#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

class FileSystemEventHandler:
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None: ...

class FileSystemEvent: ...
class DirModifiedEvent(FileSystemEvent): ...
class FileModifiedEvent(FileSystemEvent): ...
