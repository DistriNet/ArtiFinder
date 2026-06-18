#!/usr/bin/env python3
"""
Artifinder CLI - Discover artifacts for a single research paper.
"""

import argparse
import json
import logging
import pathlib
import sys
from typing import Any

import requests

from artifinder.links.parsing import LinkParser
from artifinder.links import ranking
from artifinder.links.ranking import rules
from artifinder.model import Paper, PaperTitle
from artifinder.util.log import get_logger
from artifinder.util.session import create_session

IGNORE_DOMAINS = [
    "dl.acm.org", "springer.com", "arxiv.org", "usenix.org", "ieee.org",
    "crossmark.crossref.org", "wikipedia.org", "archive.org",
    "ndss-symposium.org", "eprint.iacr.org", "ia.cr", "doi.org"
]

def get_ranking_phases(session: requests.Session, year: int | None = None):
    """Get all ranking phases."""
    phases = []
    
    # Phase 1: Basic parseability
    phases.append(ranking.RawPhase((rules.base.Parseable(),)))
    
    # Phase 2: Filter domains and joined sentences
    phases.append(ranking.UrlPhase(
        (
            rules.url.JoinedSentence(),
            *(rules.url.NotDomain(domain) for domain in IGNORE_DOMAINS),
        )
    ))
    
    # Phase 3: Check if host exists
    phases.append(ranking.UrlPhase((rules.url.HostExists(),)))
    
    # Phase 4: Identify likely artifact hosts
    phases.append(ranking.UrlPhase(
        (
            rules.url.MaybeJoinedSentence(),
            rules.url.GithubRepo(),
            rules.url.GithubStable(),
            rules.url.DoiZenodo(),
            rules.url.ZenodoArchive(),
            rules.url.Domain("gitlab.com", 10, True),
            rules.url.Domain("github.io", 10),
            rules.url.Domain("bitbucket.org", 10),
        )
    ))
    
    # Phase 5: Location-based rules
    phases.append(ranking.LocationPhase(
        (
            rules.location.TitleInUrl(),
            rules.location.LocationInPaper(),
            rules.location.LinkParagraphContext(),
        )
    ))
    
    # Phase 6: Request-based rules
    request_rules = [
        rules.request.FailedRequest(),
        rules.request.TitleInContent(),
        rules.request.AuthorInContent(),
        rules.request.PartialTitleInContent(),
        rules.request.Citation(),
        rules.url.Domain("eprint.iacr.org", -50, True),
        rules.url.Domain("ia.cr", -50, True),
        *(rules.request.FinalNotDomain(domain) for domain in IGNORE_DOMAINS),
    ]
    
    if year:
        request_rules.append(rules.request.Created(year))
        
    phases.append(ranking.RequestPhase(tuple(request_rules), session))
    
    return phases

def parse_metadata(args) -> dict[str, Any]:
    """Parse metadata from CLI or JSON file."""
    metadata = {}
    
    if args.json:
        try:
            with open(args.json, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"Error reading JSON file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # CLI args override JSON
    if args.title:
        metadata["title"] = args.title
    if args.authors:
        metadata["authors"] = [a.strip() for a in args.authors.split(",")]
    if args.year:
        metadata["year"] = args.year
    if args.conf:
        metadata["conference"] = args.conf
        
    # Validation
    if "title" not in metadata:
        metadata["title"] = "Unknown Paper"
        
    if "authors" not in metadata:
        metadata["authors"] = []
    elif isinstance(metadata["authors"], str):
        metadata["authors"] = [a.strip() for a in metadata["authors"].split(",")]
        
    return metadata

def run_pipeline(pdf_path: pathlib.Path, metadata: dict[str, Any], logger: logging.Logger):
    """Run the artifact discovery pipeline."""
    title = PaperTitle(metadata["title"])
    paper = Paper(
        title=title,
        authors=metadata.get("authors", []),
        pdf_link=str(pdf_path) if pdf_path.exists() else None
    )
    
    # Step 1: Extract links
    logger.info("Extracting links from PDF...")
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return None
        
    parser = LinkParser([(pdf_path, paper)])
    parsed_papers = parser.run()
    
    if not parsed_papers:
        logger.warning("No links extracted from paper.")
        return None
        
    parsed_paper = parsed_papers[0]
    logger.info(f"Extracted {len(parsed_paper.links)} links from paper.")
    # Step 2: Rank links
    logger.info("Ranking links...")
    session = create_session()
    ranker = ranking.Ranker()
    
    year = metadata.get("year")
            
    for phase in get_ranking_phases(session, year):
        ranker.register_phase(phase)
        
    ranked_links = ranker.rank_links(parsed_paper.links, parsed_paper, pdf_path)
            
    return {
        "paper": paper,
        "parsed_paper": parsed_paper,
        "ranked_links": ranked_links,
    }

def main():
    parser = argparse.ArgumentParser(description="Artifinder CLI - Discover artifacts for a single paper")
    parser.add_argument("--pdf", required=True, help="Path to the paper PDF file")
    parser.add_argument("--title", help="Paper title")
    parser.add_argument("--authors", help="Comma-separated authors")
    parser.add_argument("--year", type=int, help="Publication year")
    parser.add_argument("--conf", help="Conference name (e.g., usenix, ccs, ndss, sp)")
    parser.add_argument("--json", help="Path to JSON file with metadata")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose operation")
    parser.add_argument("-q", "--quiet", action="store_true", help="Disable all logging")
    
    args = parser.parse_args()
    
    # Set up logging
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    if args.quiet:
        level = logging.ERROR
    
    logger = get_logger(level)
    
    metadata = parse_metadata(args)
    pdf_path = pathlib.Path(args.pdf).resolve()
    
    results = run_pipeline(pdf_path, metadata, logger)
    
    if not results:
        logger.error("Pipeline failed to produce results.")
        sys.exit(1)
        
    ranked_links = results["ranked_links"]
    
    # Top artifact candidate
    discovered_artifact = None
    if ranked_links and ranked_links[0].score >= 20:
        discovered_artifact = ranked_links[0]
        
    # Prepare output
    output_data = {
        "title": str(results["paper"].title),
        "authors": results["paper"].authors,
        "year": metadata.get("year"),
        "conference": metadata.get("conf"),
        "pdf_path": str(pdf_path),
        "links": [link.to_dict() for link in ranked_links],
        "discovered_artifact": discovered_artifact.link if discovered_artifact else None,
        
    }
    
    # Print or save
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Results saved to {args.output}")
    else:
        print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    main()
