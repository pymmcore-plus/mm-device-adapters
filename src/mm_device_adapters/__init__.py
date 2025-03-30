"""Micro-Manager drivers package.

This package provides pre-compiled shared libraries for Micro-Manager.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("mm_device_adapters")
except PackageNotFoundError:
    __version__ = "0.0.0"
