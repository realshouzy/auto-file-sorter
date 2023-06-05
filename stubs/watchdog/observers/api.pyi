#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from watchdog.events import FileSystemEventHandler
from watchdog.utils import BaseThread

class EventDispatcher(BaseThread):
    def stop(self) -> None: ...

class BaseObserver(EventDispatcher):
    def schedule(
        self,
        event_handler: FileSystemEventHandler,
        path: str | Path,
        recursive: bool = False,
    ) -> ObservedWatch: ...
    def start(self) -> None: ...

class ObservedWatch: ...

class BaseObserverSubclassCallable(Protocol):
    def __call__(self, timeout: float = ...) -> BaseObserver: ...
