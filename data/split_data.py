#!/usr/bin/env python3
"""Split data JSON into per-conference-year YAML files."""

import argparse
import json
import yaml
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path("data.json")
OUTPUT_DIR = Path("by_conference")
EDITION_BASE_YEAR = 2000

DEFAULT_KEEP_FIELDS = [
    "title",
    "authors",
    "page_link",
    "discovered_artifact.link",
]


def parse_field_specs(specs):
    """
    Build a selection tree from dot-notation field specs.

    "title"                   -> {"title": None}
    "discovered_artifact.link"-> {"discovered_artifact": {"link": None}}

    None means "keep the entire value as-is".
    A dict means "keep only these named sub-fields".
    If a bare key and a dotted sub-key are both present (e.g. "foo" and
    "foo.bar"), the bare key wins and the whole value is kept.
    """
    tree = {}
    for spec in specs:
        _insert(tree, spec.split("."))
    return tree


def _insert(node, parts):
    key = parts[0]
    if len(parts) == 1:
        node[key] = None  # keep everything at this level
    else:
        if node.get(key) is None and key in node:
            return  # bare key already set; don't restrict further
        if key not in node:
            node[key] = {}
        _insert(node[key], parts[1:])


def extract_fields(obj, tree):
    """
    Recursively extract fields from a dict according to the selection tree."""
    result = {}
    for key, subtree in tree.items():
        val = obj.get(key)
        if subtree is None:
            result[key] = val
        elif isinstance(val, dict):
            if len(subtree) == 1:
                sub_key = next(iter(subtree))
                sub_res = extract_fields(val, subtree)
                result[key] = sub_res[sub_key]
            else:
                result[key] = extract_fields(val, subtree)
        else:
            result[key] = None
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split data/data.json into per-conference-year YAML files."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=INPUT_FILE,
        metavar="FILE",
        help="Path to the input JSON file (default: %(default)s).",
    )
    parser.add_argument(
        "--only-with-artifact",
        action="store_true",
        default=False,
        help="Only include papers that have a 'discovered_artifact' field.",
    )
    parser.add_argument(
        "--artifact-score",
        type=float,
        default=None,
        metavar="THRESHOLD",
        help=(
            "Include an 'artifacts_discovered' list in each output entry, "
            "containing all links scoring at or above THRESHOLD, ordered "
            "from highest to lowest score."
        ),
    )
    parser.add_argument(
        "--fields",
        nargs="+",
        metavar="FIELD",
        default=DEFAULT_KEEP_FIELDS,
        help=(
            "Fields to keep in the output. Use dot notation for sub-fields "
            "(e.g. discovered_artifact.link). Defaults to all standard fields."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    field_tree = parse_field_specs(args.fields + ["validated"])
    only_with_artifact = args.only_with_artifact
    artifact_score = args.artifact_score

    with open(args.input) as f:
        data = json.load(f)

    groups: dict[tuple[str, int], list[dict]] = {}
    conf_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for paper in data:
        conf = paper["conference"]
        paper["validated"] = False
        year = EDITION_BASE_YEAR + int(paper["edition"])
        if only_with_artifact and "discovered_artifact" not in paper:
            conf_stats[conf][1] += 1
            continue
        conf_stats[conf][0] += 1
        entry = extract_fields(paper, field_tree)
        if artifact_score is not None:
            qualifying = [
                link
                for link in paper.get("links", [])
                if isinstance(link.get("score"), (int, float))
                and link["score"] >= artifact_score
            ]
            qualifying.sort(key=lambda link: link["score"], reverse=True)
            validated = entry.pop("validated")
            entry["artifacts_discovered"] = list(
                dict.fromkeys(link["link"] for link in qualifying)
            )
            entry["validated"] = validated
        groups.setdefault((conf, year), []).append(entry)

    for (conf, year), papers in sorted(groups.items()):
        out_dir = OUTPUT_DIR / conf
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{year}.yaml"
        with open(out_path, "w") as f:
            yaml.dump(papers, f, allow_unicode=True, sort_keys=False)
        print(f"  {conf}/{year}.yaml  ({len(papers)} entries)")

    print()
    print(f"{'Conference':<12} {'kept':>6} {'dropped':>8} {'total':>7}")
    print("-" * 36)
    total_kept = total_dropped = 0
    for conf in sorted(conf_stats):
        kept, dropped = conf_stats[conf]
        total_kept += kept
        total_dropped += dropped
        print(f"{conf:<12} {kept:>6} {dropped:>8} {kept + dropped:>7}")
    print("-" * 36)
    print(f"{'TOTAL':<12} {total_kept:>6} {total_dropped:>8} {total_kept + total_dropped:>7}")


if __name__ == "__main__":
    main()
