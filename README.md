# mm-device-adapters

Pre-compiled libraries for Micro-Manager.

This is a metapackage that provides pre-compiled Micro-Manager shared libraries
for Windows and macOS (x86_64 only).

## Installation

```bash
pip install mm-device-adapters
```

## Usage

This package only provides the shared libraries, which will be installed to the `mm-install` directory in your site-packages folder.

## Building

This package is built using [cibuildwheel](https://cibuildwheel.readthedocs.io/). To build the wheels:

```bash
pip install cibuildwheel
python -m cibuildwheel
```