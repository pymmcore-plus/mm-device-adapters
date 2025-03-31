from __future__ import annotations

import ctypes
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.request
from functools import cache
from itertools import chain
from pathlib import Path
from platform import machine, system
from urllib.request import urlopen, urlretrieve

import certifi

PLATFORM = system()
MACH = machine()
BASE_URL = "https://download.micro-manager.org"
APPLE_SILICON = PLATFORM == "Darwin" and MACH == "arm64"
if PLATFORM not in ("Darwin", "Windows") or APPLE_SILICON:
    msg = f"Unsupported platform/architecture: {PLATFORM}/{MACH}"
    raise RuntimeError(msg)

plat = {"Darwin": "Mac", "Windows": "Windows"}.get(PLATFORM)
DOWNLOADS_URL = f"{BASE_URL}/nightly/2.0/{plat}/"


def _win_install(exe: Path, dest: Path) -> None:
    tmp_dest = Path(tempfile.mkdtemp())
    cmd = [str(exe), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", f"/DIR={tmp_dest}"]
    subprocess.run(cmd, check=True)
    for lib in chain(tmp_dest.rglob("*.dll"), tmp_dest.rglob("*.exe")):
        if any(x in str(lib) for x in ("jre", "ImageJ", "java")):
            continue
        lib_dest = dest / lib.relative_to(tmp_dest)
        lib_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(lib, lib_dest)


def _mac_install(dmg: Path, dest: Path) -> None:
    """Install Micro-Manager `dmg` to `dest`."""
    # with progress bar, mount dmg
    proc = subprocess.run(
        ["hdiutil", "attach", "-nobrowse", str(dmg)],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        msg = f"\nError mounting {dmg.name}:\n{proc.stderr.decode()}"
        raise RuntimeError(msg)

    # get mount point
    disk_id, *_, volume = proc.stdout.splitlines()[-1].decode().split("\t")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        # with progress bar, mount dmg
        try:
            src = next(Path(volume).glob("Micro-Manager*"))
        except StopIteration:
            msg = (
                "\nError: Could not find Micro-Manager in dmg.\n"
                "Please report this at https://github.com/pymmcore-plus/"
                "pymmcore-plus/issues/new"
            )
            raise RuntimeError(
                msg,
            )

        for lib in src.glob("libmmgr*"):
            shutil.copy(lib, dest / lib.name)
    finally:
        subprocess.run(
            ["hdiutil", "detach", disk_id.strip()],
            check=True,
            capture_output=True,
        )

    # fix gatekeeper ... may require password?  But better if sudo not needed.
    cmd = ["xattr", "-r", "-d", "com.apple.quarantine", str(dest)]
    subprocess.run(cmd, check=False)


@cache
def available_versions() -> dict[str, str]:
    """Return a map of version -> url available for download."""
    # Set up SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(DOWNLOADS_URL, context=ssl_context) as resp:
        html = resp.read().decode("utf-8")

    all_links = re.findall(r"href=\"([^\"]+)\"", html)
    delim = "_" if PLATFORM == "Windows" else "-"
    return {
        ref.rsplit(delim, 1)[-1].split(".")[0]: BASE_URL + ref
        for ref in all_links
        if ref != "/" and "32bit" not in ref
    }


def _download_url(url: str, output_path: Path, show_progress: bool = True) -> None:
    """Download `url` to `output_path` with a nice progress bar."""
    # Create a context using system certificates from certifi
    ctx = ssl.create_default_context(cafile=certifi.where())

    # Create an opener that uses our SSL context
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    urllib.request.install_opener(opener)

    # Download the file
    urlretrieve(url=url, filename=output_path)


def install(dest: Path | str | None = None, release: str = "latest") -> tuple[str, str]:
    """Install Micro-Manager to `dest`.

    Parameters
    ----------
    dest : Path | str, optional
        Where to install Micro-Manager. For cibuildwheel, this should be the package
        directory where the wheel contents will be located.
    release : str, optional
        Which release to install, by default "latest-compatible". Should be a date in the form
        YYYYMMDD, "latest" to install the latest nightly release, or "latest-compatible"
        to install the latest nightly release.

    """
    if not dest:
        dest = Path(__file__).parent / "src" / "mm_device_adapters" / "libs"

    available = available_versions()
    if release == "latest":
        release = sorted(available)[-1]
    elif release not in available:
        n = 30
        avail = ", ".join(sorted(available)[-n:]) + " ..."
        msg = f"Release {release!r} not found. Last {n} releases:\n{avail}"
        raise RuntimeError(
            msg,
        )
    url = available[release]

    with tempfile.TemporaryDirectory() as tmpdir:
        # download
        installer = Path(tmpdir) / url.split("/")[-1]
        _download_url(url=url, output_path=installer)

        # install
        dest = Path(dest).expanduser().resolve()
        if PLATFORM == "Darwin":
            _mac_install(installer, dest)
        elif PLATFORM == "Windows":
            # For windows, directly install to destination directory
            _win_install(installer, dest)

    div = str(get_device_interface_version(dest))
    return div, release


def get_device_interface_version(lib_path: Path) -> int:
    """Return the device interface version from the given library path."""
    lib_path = next(f for f in lib_path.glob("*_dal_*"))

    if sys.platform.startswith("win"):
        lib = ctypes.WinDLL(lib_path)
    else:
        lib = ctypes.CDLL(lib_path)

    try:
        func = lib.GetDeviceInterfaceVersion
    except AttributeError:
        msg = f"Function 'GetDeviceInterfaceVersion' not found in {lib_path}"
        raise RuntimeError(msg) from None

    func.restype = ctypes.c_long
    func.argtypes = []
    return func()  # type: ignore[no-any-return]


if __name__ == "__main__":
    install(sys.argv[1])
