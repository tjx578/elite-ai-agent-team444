"""Caller-trusted test-subject loading from explicit bytes, never cached code.

This loader does not authenticate its input. Tests choose the trusted source;
production collector authentication remains the validator's responsibility.
"""
from __future__ import annotations

import importlib.abc
from pathlib import Path
from types import CodeType, ModuleType


class _TestBufferLoader(importlib.abc.InspectLoader):
    def __init__(self, name: str, source: bytes, origin: str) -> None:
        self._name, self._source, self._origin = name, bytes(source), origin

    def get_source(self, fullname: str) -> str:
        if fullname != self._name:
            raise ImportError("TEST_MODULE_NAME")
        return self._source.decode("utf-8", errors="strict")

    def get_code(self, fullname: str) -> CodeType:
        if fullname != self._name:
            raise ImportError("TEST_MODULE_NAME")
        return compile(self._source, self._origin, "exec", dont_inherit=True)


def load_subject(path: Path, name: str) -> ModuleType:
    module = ModuleType(name)
    module.__file__ = str(path)
    _TestBufferLoader(name, path.read_bytes(), str(path)).exec_module(module)
    return module
