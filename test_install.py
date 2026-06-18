#!/usr/bin/env python3
"""Check that all packages in requirements.txt are installed, plus poppler-glib/pygobject."""

import importlib
import subprocess
import sys
from pathlib import Path

REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"

# Map from pip package name -> importable module name (when they differ)
IMPORT_OVERRIDES = {
    "beautifulsoup4": "bs4",
    "pyyaml": "yaml",
    "pygobject": "gi",
    "dnspython": "dns",
    "python-dotenv": "dotenv"
}


def pkg_to_module(pkg_name: str) -> str:
    key = pkg_name.lower()
    if key in IMPORT_OVERRIDES:
        return IMPORT_OVERRIDES[key]
    # Default: lowercase, replace hyphens with underscores
    return pkg_name.lower().replace("-", "_")



def parse_requirements(path: Path) -> list[str]:
    packages = []
    if not path.exists():
        print(f"[WARN] {path} not found – skipping requirements.txt checks.")
        return packages
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Strip version specifiers and extras
        pkg = line.split("[")[0]
        for sep in ("==", ">=", "<=", "!=", "~=", ">", "<", "@"):
            pkg = pkg.split(sep)[0]
        pkg = pkg.strip()
        if pkg:
            packages.append(pkg)
    return packages


def check_import(module_name: str) -> tuple[bool, str]:
    try:
        importlib.import_module(module_name)
        return True, ""
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"unexpected error: {e}"


def check_poppler_gi() -> list[tuple[str, bool, str]]:
    results = []

    # 1. gi itself
    ok, err = check_import("gi")
    results.append(("pygobject (gi)", ok, err))
    if not ok:
        results.append(("gi.require_version / Poppler", False, "gi not available"))
        return results

    # 2. gi.repository.GLib
    try:
        from gi.repository import GLib
        results.append(("gi.repository.GLib", True, ""))
    except Exception as e:
        results.append(("gi.repository.GLib", False, str(e)))

    # 3. Poppler via gi
    try:
        import gi
        gi.require_version("Poppler", "0.18")
        from gi.repository import Poppler
        results.append(("gi.repository.Poppler (0.18)", True, ""))
    except Exception as e:
        results.append(("gi.repository.Poppler (0.18)", False, str(e)))

    return results

def main():
    passed = []
    failed = []

    packages = parse_requirements(REQUIREMENTS_FILE)
    for pkg in packages:
        module = pkg_to_module(pkg)
        ok, err = check_import(module)
        label = f"{pkg} (import {module})"
        if not ok:
            print(f"  [FAILED] {label}" + (f"  — {err}" if err else ""))
        (passed if ok else failed).append(label)

    for label, ok, err in check_poppler_gi():
        if not ok:
            print(f"  [FAILED] {label}" + (f"  — {err}" if err else ""))
        (passed if ok else failed).append(label)

if __name__ == "__main__":
    main()