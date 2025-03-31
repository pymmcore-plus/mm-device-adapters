# mm-device-adapters

[![License](https://img.shields.io/pypi/l/mm-device-adapters.svg?color=green)](https://github.com/mm-device-adapters/mm-device-adapters/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mm-device-adapters.svg?color=green)](https://pypi.org/project/mm-device-adapters)
[![Build](https://github.com/pymmcore-plus/mm-device-adapters/actions/workflows/ci.yml/badge.svg)](https://github.com/pymmcore-plus/mm-device-adapters/actions/workflows/ci.yml)

Pre-compiled libraries for Micro-Manager.

This is a metapackage that provides pre-compiled Micro-Manager shared libraries
for Windows and macOS (x86_64 only).

These are the same libraries available at
<https://micro-manager.org/Micro-Manager_Nightly_Builds> but have been stripped
of everything *but* the device adapter shared libraries (i.e. they lack
everything related to the java application).

The version will be a 4-digit number, such as `73.2025.3.28`.
The first number (e.g. `73`) is the device interface for which
the libraries were compiled, and the next three (e.g. `2025.3.28`)
are the date of the nightly build in `YYYY.M?M.D?D`.

When using with [pymmcore](https://github.com/micro-manager/pymmcore), the
device interface must match the device interface version (the fourth number)
in the pymmcore version

## Installation

```bash
pip install mm-device-adapters
```

## Usage

The libraries will be installed to `mm_device_adapters/lib` directory
in your site-packages folder.  There is also a convenience function
(`device_adapter_path`) to access this:

```py
from mm_device_adapters import device_adapter_path
import pymmcore

mmc = pymmcore.CMMCore()
mmc.setDeviceAdapterSearchPaths([device_adapter_path()])
```
