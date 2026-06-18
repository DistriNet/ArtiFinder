__all__ = [
    "Conference",
    "Paper",
    "PaperTitle",
    "ArtifactBadge",
    "ACMArtifactBadge",
    "UsenixArtifactBadge",
    "parse_config",
    "dump_config",
]

import json
import sys
from datetime import datetime
from typing import Any, Generic, TypedDict, TypeVar, overload

from .badge import (
    ACMArtifactBadge,
    ArtifactBadge,
    UsenixArtifactBadge,
)
from .conference import Conference
from .paper import Paper, PaperTitle

_PT = TypeVar("_PT", bound=Paper, covariant=True)


class Config(TypedDict, Generic[_PT]):
    timestamp: str
    conference: str
    edition: str
    paper_total: int
    paper_path : str
    papers: list[_PT]


@overload
def parse_config(config_path: str, typ: type[_PT]) -> Config[_PT]: ...


@overload
def parse_config(config_path: str, typ: type[Paper] = Paper) -> Config[Paper]: ...


def parse_config(config_path: str, typ: type[_PT] = Paper) -> Config[_PT]:  # type: ignore[assignment]
    with open(config_path) as f:
        raw: dict[str, Any] = json.load(f)

    papers: list[dict[str, str | list[str | dict[str, Any]] | dict[str, str]]] = raw["papers"]

    result: Config[_PT] = {
        "timestamp": raw["timestamp"],
        "conference": raw["conference"],
        "edition": raw["edition"],
        "paper_total": raw["paper_total"],
        "paper_path": raw["paper_path"],
        "papers": [],
    }
    for p in papers:
        result["papers"].append(typ.from_dict(p))  # type: ignore[arg-type]

    return result


def dump_config(conf: str, edition: str, papers: list[Paper], timestamp: str | None = None, paper_path: str | None = None) -> None:
    d = {
        "timestamp": timestamp or datetime.now().astimezone().isoformat(),
        "conference": conf,
        "edition": edition,
        "paper_path": paper_path,
        "paper_total": len(papers),
        "papers": list(map(lambda x: x.to_dict(), papers)),
    }
    json.dump(d, sys.stdout, indent=4)

