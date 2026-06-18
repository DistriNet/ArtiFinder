import dataclasses
from typing import Any, override

from artifinder import model


@dataclasses.dataclass(slots=True)
class ParsedLink:
    link: str
    locations: list[int]
    occurrences: int
    page: int
    page_length: int
    annotation: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ParsedLink":
        return cls(
            link=d["link"],
            locations=d.get("locations"),
            occurrences=d.get("occurrences"),
            page=d.get("page"),
            page_length=d.get("page_length"),
            annotation=d.get("annotation"),
        )

    def __str__(self) -> str:
        return self.link


@dataclasses.dataclass
class ParsedPaper(model.Paper):
    links: list[ParsedLink] = dataclasses.field(default_factory=list)
    pages: int | None = dataclasses.field(default=None)
    discovered_artifact: ParsedLink | None = dataclasses.field(default=None)

    @classmethod
    def from_paper(cls, paper: model.Paper, links: list[ParsedLink], pages: int) -> "ParsedPaper":
        return cls(
            title=paper.title,
            page_link=paper.page_link,
            pdf_link=paper.pdf_link,
            appendix_link=paper.appendix_link,
            badges=paper.badges.copy(),
            links=links,
            pages=pages,
        )

    @override
    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()

        d["links"] = [link.to_dict() for link in self.links]
        d["pages"] = self.pages
        d["discovered_artifact"] = self.discovered_artifact.to_dict() if self.discovered_artifact else None
        return d

    @classmethod
    def from_dict(cls, d: dict[str, str | list[str | dict[str, Any]] | dict[str, str]]) -> "ParsedPaper":
        p = super().from_dict(d)
        assert isinstance(p, ParsedPaper)

        p.pages = d.get("pages")  # type: ignore[assignment]
        if "links" in d:
            p.links = [ParsedLink.from_dict(pl) for pl in d["links"]]  # type: ignore[arg-type]
        if "discovered_artifact" in d and d["discovered_artifact"] is not None:
            p.discovered_artifact = ParsedLink.from_dict(d["discovered_artifact"])
        return p
