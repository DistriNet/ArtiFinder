import dataclasses
from typing import Any, override
from artifinder.links.parsing.base import ParsedLink, ParsedPaper

@dataclasses.dataclass(frozen=True, slots=True)
class BreakDownEntry:
    name: str
    value: float
    
    def to_dict(self):
        return dataclasses.asdict(self)


class RankedLink(ParsedLink):
    score: float
    breakdown: list[BreakDownEntry]

    def __post_init__(self) -> None:
        if len(self.breakdown) != 0 and isinstance(self.breakdown[0], dict):
            self.breakdown = [BreakDownEntry(**m) for m in self.breakdown]  # type: ignore[arg-type]
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RankedLink":
        p = super().from_dict(data)
        assert isinstance(p, ParsedLink)
        if "score" in data:
            p.score = data["score"]
        if "breakdown" in data:
            p.breakdown = [BreakDownEntry(**m) for m in data["breakdown"]]
        return p
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "score": getattr(self, "score", None),
            "breakdown": [bd.to_dict() for bd in getattr(self, "breakdown", [])],
        }
        
class RankedPaper(ParsedPaper):
    links: list[RankedLink] = dataclasses.field(default_factory=list)
    discovered_artifact: RankedLink | None = dataclasses.field(default=None)
    
    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RankedPaper":
        p = super().from_dict(d)
        assert isinstance(p, ParsedPaper)
        if "links" in d:
            ranked_links = [RankedLink.from_dict(rl) for rl in d["links"]]
            p.links = ranked_links  # type: ignore[assignment]
        if "discovered_artifact" in d and d["discovered_artifact"] is not None:
            p.discovered_artifact = RankedLink.from_dict(d["discovered_artifact"])  # type: ignore[assignment]
        return p
    
    @override
    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["links"] = [link.to_dict() for link in self.links]
        d["discovered_artifact"] = self.discovered_artifact.to_dict() if self.discovered_artifact else None
        return d