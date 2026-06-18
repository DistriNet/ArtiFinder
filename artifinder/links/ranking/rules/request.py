import itertools
import logging
import os
import re
import warnings
from abc import ABC
from dataclasses import dataclass, field

import bibtexparser
import bibtexparser.middlewares.middleware
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from regex import regex
from urllib3.util import Url

from artifinder.links.ranking.rules.base import AbstractRule, RuleContext
from artifinder.scraper.util import TitleMatcher
from dotenv import load_dotenv

PatternType = re.Pattern[str] | regex.Pattern[str]
load_dotenv()

@dataclass(slots=True)
class RequestRuleContext(RuleContext):
    url: Url
    session: requests.Session
    response: requests.Response | None

    _cached_content: BeautifulSoup | None = field(init=False, default=None)

    def content(self) -> BeautifulSoup | None:
        if self.response is None:
            return None
        if self._cached_content is not None:
            return self._cached_content
        if not self.response.content:
            return None

        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        self._cached_content = BeautifulSoup(self.response.content, "lxml")

        return self._cached_content


class RequestBaseRule(AbstractRule[RequestRuleContext], ABC):
    pass


@dataclass
class FailedRequest(RequestBaseRule):
    """
    Decreases score for failed requests.
    """

    score: int = -20

    def eval(self, ctx: RequestRuleContext) -> bool:
        if ctx.response is None:
            return False

        return not ctx.response.ok

@dataclass
class FinalNotDomain(RequestBaseRule):
    host: str
    score: int = -100

    def eval(self, ctx: RequestRuleContext) -> bool:
        final_url = ctx.response.url if ctx.response else str(ctx.url)
        parsed_final_url = requests.utils.urlparse(final_url)
        if parsed_final_url.netloc is None:
            return False
        return parsed_final_url.netloc.replace("www.", "") == self.host
    
@dataclass
class AuthorInContent(RequestBaseRule):
    """
    Searches for a reference to the author on the website.
    """

    score: int = 10

    def eval(self, ctx: RequestRuleContext) -> bool:
        if ctx.root.paper is None or (content := ctx.content()) is None:
            return False
        found_authors = 0
        for author in ctx.root.paper.authors:
            pat = re.compile(rf"({re.escape(author)})", re.I)
            if pat.search(content.get_text(separator=" ", strip=True)) is not None:
                found_authors += 1
        ctx.score_modifier = found_authors / len(ctx.root.paper.authors) if ctx.root.paper.authors else 0.0
        return found_authors > 0

@dataclass
class TitleInContent(RequestBaseRule):
    """
    Searches for a reference to the title on the website.
    """

    score: int = 20

    def eval(self, ctx: RequestRuleContext) -> bool:
        if ctx.root.paper is None or (content := ctx.content()) is None:
            return False

        pat = TitleMatcher.title_pattern(str(ctx.root.paper.title), False)

        return pat.search(content.get_text(separator=" ", strip=True)) is not None


@dataclass
class PartialTitleInContent(RequestBaseRule):
    """
    Searches for a reference to the title on the website.
    """

    score: float = 5.0

    def eval(self, ctx: RequestRuleContext) -> bool:
        if ctx.root.paper is None or (content := ctx.content()) is None:
            return False

        pat = re.compile(rf"({re.escape(ctx.root.paper.title.popular_title)})", re.I)

        count = sum(1 for _ in itertools.islice(pat.finditer(content.get_text(separator=" ", strip=True)), 19))
        ctx.score_modifier = count / 20.0

        return count > 0

@dataclass    
class Created(RequestBaseRule):
    """
    Checks for Github and Zenodo, at what time the repos are created. Should not be earlier than 2 years from conference.
    """
    year: int
    score: int = -20

    def eval(self, ctx: RequestRuleContext) -> bool:
        if re.match(r"(.*)github\.com/[^/]+/[^/]+", str(ctx.link)):
            (_, owner, repo) = re.match(r"(.*)github\.com/([^/]+)/([^/]+)", str(ctx.link)).groups()
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                return False
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
            if not response.ok:
                return False
            data = response.json()
            created_at = data.get("created_at")
            if not created_at:
                return False
            created_year = int(created_at.split("-")[0])
            return created_year + 2 < self.year

        elif re.match(r"zenodo\.org/records/[^/]+", str(ctx.link)):
            if not ctx.response or not ctx.response.ok or (content := ctx.content()) is None:
                return False
            publication_date_elem = content.find("span", {"title": "Publication date"}).text
            pub_year = re.search(r"\b\d{4}\b", publication_date_elem)
            if not pub_year:
                return False
            return int(pub_year.group(0)) + 2 < self.year
        else:
            return False

@dataclass
class Citation(RequestBaseRule):
    """
    Searches for bibtex citations and checks if the entry matches the paper.
    """

    score: int = 50
    cite_rex: PatternType = field(init=False)

    parse_stack: list[bibtexparser.middlewares.middleware.Middleware] = field(init=False)

    def __post_init__(self) -> None:
        self.parse_stack = [
            self._restore_failed_blocks_middleware(),
            bibtexparser.middlewares.ResolveStringReferencesMiddleware(allow_inplace_modification=True),
            bibtexparser.middlewares.RemoveEnclosingMiddleware(allow_inplace_modification=True),
            # Entries are sometimes double enclosed
            bibtexparser.middlewares.RemoveEnclosingMiddleware(allow_inplace_modification=True),
        ]
        self.cite_rex = self._build_cite_rex()

    @staticmethod
    def _build_cite_rex() -> PatternType:
        ws = r"""[^\S\r\n]*"""
        entry = r"""@[a-zA-Z]+{[^~\\"#'(),={}%\s]+,"""
        field_key = r"""[^~\\"#'(),={}%\s]+"""
        field_val = (
            r"""(?:[^{}"\s][^{}\r\n]+|(?:{(?:"""
            + rf"(?!.*{entry})"
            + r""".+(?:$\s|(?=}\s*,?\s*}?\s*$)))+})+|"(?:"""
            + rf"(?!.*{entry})"
            + r"""[^"\r\n]+(?:$\s|(?="\s*,?\s*}?\s*$)))+")"""
        )
        fieldkv = rf"""^{ws}{field_key}{ws}={ws}{field_val}{ws}"""

        return re.compile(rf"""{ws}{entry}{ws}$\s(?:{fieldkv},{ws}$\s)*{fieldkv},?{ws}\s?{ws}}}""", re.M)

    def _restore_failed_blocks_middleware(self) -> bibtexparser.middlewares.LibraryMiddleware:
        def transform(library: bibtexparser.Library) -> bibtexparser.Library:
            block: bibtexparser.model.ParsingFailedBlock
            for block in library.failed_blocks:
                err_block = block.ignore_error_block
                if isinstance(err_block, bibtexparser.model.Entry):
                    library.add(err_block)
            return library

        m = bibtexparser.middlewares.LibraryMiddleware()
        m.transform = transform  # type: ignore[method-assign]

        return m

    def _parse(self, bibtex_str: str) -> bibtexparser.Library:
        _logger = logging.getLogger()
        saved_val = _logger.disabled
        try:
            _logger.disabled = True
            # bibtexparser uses the root logger...
            return bibtexparser.parse_string(bibtex_str, parse_stack=self.parse_stack)
        finally:
            _logger.disabled = saved_val

    def eval(self, ctx: RequestRuleContext) -> bool:
        if ctx.root.paper is None or (content := ctx.content()) is None:
            return False

        matcher: TitleMatcher[str] | None = None
        for m in self.cite_rex.finditer(str(content)):  # citation is sometimes in data attr or js
            for entry in self._parse(m.group(0)).entries:
                if (title_entry := entry.get("title")) is None:
                    continue

                matcher = matcher or TitleMatcher([str(ctx.root.paper.title)])

                val = " ".join([s.strip() for s in title_entry.value.splitlines() if s])
                if matcher.match(val) is not None:
                    return True

        return False
