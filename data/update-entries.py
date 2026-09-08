#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

import yaml


def parse_args():
    parser = argparse.ArgumentParser(
        description="Copy selected fields from src YAML files into matching dest YAML files."
    )
    parser.add_argument(
        "-src",
        type=Path,
        required=True,
        metavar="DIR",
        help="Source directory (e.g. by_conference), containing conference/year.yaml files.",
    )
    parser.add_argument(
        "-dest",
        type=Path,
        required=True,
        metavar="DIR",
        help="Destination directory (e.g. ../../artifinder-data/data) with matching structure.",
    )
    parser.add_argument(
        "-fields",
        nargs="+",
        required=True,
        metavar="FIELD",
        help="Top-level field names to copy from src into dest.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    src_files = sorted(args.src.glob("*/*.yaml"))
    if not src_files:
        print(f"No YAML files found under {args.src}", file=sys.stderr)
        sys.exit(1)

    updated_files = 0
    updated_entries = 0
    skipped_files = 0

    for src_file in src_files:
        rel_path = src_file.relative_to(args.src)
        dest_file = args.dest / rel_path
        if not dest_file.exists():
            print(f"  skip {rel_path} (missing in dest)", file=sys.stderr)
            skipped_files += 1
            continue

        with open(src_file) as f:
            src_entries = yaml.safe_load(f) or []
        with open(dest_file) as f:
            dest_entries = yaml.safe_load(f) or []

        if len(src_entries) != len(dest_entries):
            print(
                f"  skip {rel_path} (entry count mismatch: "
                f"{len(src_entries)} src vs {len(dest_entries)} dest)",
                file=sys.stderr,
            )
            skipped_files += 1
            continue

        file_changed = False
        for src_entry, dest_entry in zip(src_entries, dest_entries):
            entry_changed = False
            for field in args.fields:
                new_val = src_entry.get(field)
                if dest_entry.get(field) != new_val:
                    dest_entry[field] = new_val
                    entry_changed = True
            if entry_changed:
                updated_entries += 1
                file_changed = True

        if file_changed:
            with open(dest_file, "w") as f:
                yaml.dump(dest_entries, f, allow_unicode=True, sort_keys=False)
            updated_files += 1
            print(f"  updated {rel_path}")

    print()
    print(f"Updated {updated_entries} entr{'y' if updated_entries == 1 else 'ies'} "
          f"across {updated_files} file(s); skipped {skipped_files} file(s).")


if __name__ == "__main__":
    main()
