"""
Utilities for comparing discovered links against ground truth artifacts.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

import requests
from urllib3.util import Url, parse_url

from artifinder.links.parsing import ParsedPaper
from artifinder.links.ranking import RankedLink
from artifinder.scraper.util import TitleMatcher


class GroundTruthArtifact(Protocol):
    """Protocol for ground truth artifacts that can be used for comparison."""
    title: str
    artifact_url: str


@dataclass(slots=True)
class ComparedPaper:
    """Result of comparing a paper's discovered links against ground truth."""
    title: str
    groundtruth_link: str | None
    links: tuple[RankedLink, ...]
    exact_match_index: int = field(default=-1)
    closest_partial_match_index: int = field(default=-1)
    best_match_index: int = field(default=-1)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ComparedPaper":
        for x in d["links"]:
            if "metadata" in x:
                del x["metadata"]

        return cls(
            title=d["title"],
            groundtruth_link=d["groundtruth_link"],
            links=tuple(RankedLink(**x) for x in d["links"]),
            exact_match_index=d["exact_match_index"],
            closest_partial_match_index=d["closest_partial_match_index"],
            best_match_index=d["best_match_index"],
        )


def _try_parse_url(link: str | None) -> Url | None:
    """Try to parse a URL string, returning None if parsing fails."""
    try:
        if not link:
            return None
        url = parse_url(link)
        if url.scheme is None:
            url = Url("http", url.auth, url.host, url.port, url.path, url.query, url.fragment)
        return url
    except ValueError:
        return None


def _may_match(url: Url) -> bool:
    """Check if a URL might be a valid artifact link."""
    if url.host == "github.com":
        if url.path is None:
            return False

    return True


def _normalize_url(url: Url) -> Url:
    """Normalize a URL for comparison purposes."""
    if url.host == "github.com":
        if url.path is None:
            return url
        path_parts = url.path.strip("/").split("/")
        if len(path_parts) >= 4:
            if path_parts[2] == "releases" and path_parts[3] == "tag":
                del path_parts[3]
                path_parts[2] = "tree"
        if len(path_parts) > 2:
            if path_parts[2] in ["commit"]:
                path_parts[2] = "tree"

        url = Url(
            "https",
            url.auth,
            url.host,
            url.port,
            "/".join(path_parts).removesuffix(".git").lower(),
            url.query,
            url.fragment,
        )
    return url


def _compare_paths(a: str, b: str) -> bool:
    """Check if path b is a prefix of path a."""
    sa = a.strip("/").split("/")
    sb = b.strip("/").split("/")

    if len(sb) > len(sa):
        return False

    for i in range(len(sb)):
        if sa[i] != sb[i]:
            return False

    return True


def compare_papers_to_groundtruth(
    log: logging.Logger,
    papers: list[ParsedPaper],
    links: dict[str, list[RankedLink]],
    groundtruth: list[GroundTruthArtifact],
) -> list[ComparedPaper]:
    """
    Compare discovered paper links against ground truth artifacts.
    
    Args:
        log: Logger for output messages
        papers: List of parsed papers
        links: Dictionary mapping paper IDs to their ranked links
        groundtruth: List of ground truth artifacts with title and artifact_url fields
        
    Returns:
        List of comparison results for each paper
    """
    m = TitleMatcher(groundtruth, key=lambda x: str(x.title))

    session = requests.Session()
    result = []

    for paper in papers:
        if paper.id() not in links:
            continue

        # Find all matching ground truth artifacts for this paper title
        matching_artifacts = [gt for gt in groundtruth if str(gt.title) == str(paper.title)]
        if not matching_artifacts:
            log.error("Failed to find groundtruth for paper: %s", paper.title)
            continue

        # Process each matching artifact URL
        cps = []
        for artifact in matching_artifacts:
            if not hasattr(artifact, 'artifact_url') or not artifact.artifact_url:
                log.warning("No artifact url in groundtruth %s", artifact.title)
                cps.append(ComparedPaper(str(paper.title), None, tuple(links[paper.id()])))
                continue

            artifact_url_str = artifact.artifact_url
            cp = ComparedPaper(str(paper.title), artifact_url_str, tuple(links[paper.id()]))
            cps.append(cp)

            artifact_url = _try_parse_url(artifact_url_str.lower())
            artifact_url = _normalize_url(artifact_url)
            if artifact_url is None:
                log.warning("Failed to parse artifact url: %s, paper: %s", artifact_url_str, artifact.title)
                continue

            best_match_length = -1
            for i, link in enumerate(cp.links):
                url = _try_parse_url(link.link.lower())
                if url is None:
                    continue
                url = _normalize_url(url)

                if "doi.org" in url.host and artifact_url.host != url.host:
                    r = session.head(url.url)
                    if "Location" in r.headers:
                        url = _try_parse_url(r.headers["Location"])
                if artifact_url.host != url.host:
                    continue

                if not _may_match(url):
                    continue

                if cp.exact_match_index == -1 and artifact_url.path == url.path:
                    cp.exact_match_index = i

                artifact_path = artifact_url.path or ""
                url_path = url.path or ""
                if _compare_paths(artifact_path, url_path):
                    if cp.closest_partial_match_index == -1:
                        cp.closest_partial_match_index = i
                    if len(url_path) > best_match_length:
                        best_match_length = len(url_path)
                        cp.best_match_index = i

        # Select the best comparison result using the original logic
        if not cps:
            continue

        # Prefer exact matches first
        cps_exact = sorted(filter(lambda c: c.exact_match_index != -1, cps), key=lambda c: c.exact_match_index)
        if len(cps_exact) > 0:
            result.append(cps_exact[0])
            continue

        # Then prefer best matches
        cps_best = sorted(filter(lambda c: c.best_match_index != -1, cps), key=lambda c: c.best_match_index)
        if len(cps_best) > 0:
            result.append(cps_best[0])
            continue

        # Finally, take the first comparison result
        result.append(cps[0])

    return result
