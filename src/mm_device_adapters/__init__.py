"""Micro-Manager drivers package.

This package provides pre-compiled shared libraries for Micro-Manager.
"""

import os.path
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mm-device-adapters")
except PackageNotFoundError:
    __version__ = "0.0.0.0"


def device_adapter_path() -> str:
    mm_dir = os.path.join(os.path.dirname(__file__), "libs")
    env_path = os.environ["PATH"]
    if mm_dir not in env_path:
        os.environ["PATH"] = env_path + os.pathsep + mm_dir
    return mm_dir
