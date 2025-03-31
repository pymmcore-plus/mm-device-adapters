#!/usr/bin/env python3

import json
import os
import subprocess
from collections import defaultdict


def main() -> None:
    # First get all device adapter directories
    adapter_dirs = []
    try:
        # Use find to get all subdirectories in DeviceAdapters
        result = subprocess.run(
            ["find", "DeviceAdapters", "-maxdepth", "1", "-type", "d"],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.splitlines():
            if line != "DeviceAdapters":  # Skip the parent directory
                adapter_name = os.path.basename(line)
                adapter_dirs.append(adapter_name)
    except subprocess.CalledProcessError:
        return

    # Track modification dates for each subdirectory
    changes_by_adapter = defaultdict(set)

    for adapter in adapter_dirs:
        try:
            # Get all commits that modified the specific device adapter
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--format=%ad",
                    "--date=format:%Y%m%d",
                    f"DeviceAdapters/{adapter}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Add each date to the set for this adapter
            for line in result.stdout.splitlines():
                if line.strip():
                    changes_by_adapter[adapter].add(line.strip())

        except subprocess.CalledProcessError:
            pass

    # Convert sets to sorted lists for JSON serialization (newest dates first)
    result = {
        adapter: sorted(dates, reverse=True)
        for adapter, dates in changes_by_adapter.items()
    }

    # Output the result as JSON

    # Also save to a file
    with open("device_adapter_changes.json", "w") as f:
        json.dump(result, f, indent=2)



if __name__ == "__main__":
    main()
