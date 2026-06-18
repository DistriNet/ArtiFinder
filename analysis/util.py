import json
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from urllib3.util import Url, parse_url
from urllib.parse import urlparse


DATAFILE = "data/data.json"
DATAFILEACSAC = "data/data-acsac.json"
RESULTS_FILE = "results.md"

def log_result(text):
    with open(RESULTS_FILE, "a") as f:
        f.write(f"{text}\n")

# USENIX Style Plotting Configurations
def setup_plot_style(font_size=16):
    plt.rcParams.update({
        "font.size": font_size,
        "axes.titlesize": font_size + 2,
        "axes.labelsize": font_size,
        "xtick.labelsize": font_size - 2,
        "ytick.labelsize": font_size - 2,
        "legend.fontsize": font_size - 2,
        "figure.titlesize": font_size + 4,
    })

def save_plot(fig, filename):
    plt.tight_layout()
    fig.savefig(filename, bbox_inches='tight', dpi=300)
    print(f"Saved figure to {filename}")
    plt.close(fig)

def get_data():
    with open(DATAFILE) as f:
        return json.load(f)

def get_data_acsac():
    with open(DATAFILEACSAC) as f:
        return json.load(f)

def url_matches_any_discovered_artifact(actual_url: str, links: list[dict]) -> bool:
    for link in links:
        if _urls_match(actual_url, link.get("link")):
            return True
    return False


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

def _urls_match(url1: str | None, url2: str | None) -> bool:
    """Compare two URLs using normalization and path comparison logic."""
    if not url1 or not url2:
        return url1 == url2
    
    # Direct string comparison first
    if url1 == url2:
        return True
    
    # Parse and normalize URLs
    parsed_url1 = _try_parse_url(url1.lower())
    parsed_url2 = _try_parse_url(url2.lower())
    
    if parsed_url1 is None or parsed_url2 is None:
        return False
    
    normalized_url1 = _normalize_url(parsed_url1)
    normalized_url2 = _normalize_url(parsed_url2)
    
    # Check if hosts match
    if normalized_url1.host != normalized_url2.host:
        return False
    
    # if github compare only up to user level
    if normalized_url1.host == "github.com":
        path1_parts = (normalized_url1.path or "").strip("/").split("/")
        path2_parts = (normalized_url2.path or "").strip("/").split("/")
        if len(path1_parts) < 1 or len(path2_parts) < 1:
            return False
        return path1_parts[0] == path2_parts[0]
    
    # Check exact path match
    if normalized_url1.path == normalized_url2.path:
        return True
    
    # Check path prefix match (either direction)
    path1 = normalized_url1.path or ""
    path2 = normalized_url2.path or ""
    
    return _compare_paths(path1, path2) or _compare_paths(path2, path1)

domain_colors = {
    "GitHub Repo": "#1f77b4",
    "GitHub Pages": "#ff7f0e",
    "GitLab": "#baec06",
    "Zenodo": "#2ca02c",
    "Google Sites": "#9467bd",
    "Other DOI-service": "#8c564b",
    ".edu domains": "#e377c2",
    "Other": "#7f7f7f",
}

domain_hatch = {
    "GitHub Repo": "",
    "GitHub Pages": "||",
    "GitLab": "\\\\",
    "Zenodo": "xx",
    "Google Sites": "**",
    "Other DOI-service": "..",
    ".edu domains": "++",
    "Other": "//",
}

def convert_url_to_domain(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if not domain:
        domain = urlparse("https://" + url).netloc
    if domain.endswith("doi.org"):
        if "zenodo" in url:
            domain = "Zenodo"
        elif "figshare" in url:
            domain = "Figshare"
        else:
            domain = "Other DOI-service"
    if domain == "github.com": domain = "GitHub Repo"
    if domain.endswith("github.io"): domain = "GitHub Pages"
    if domain == "gitlab.com": domain = "GitLab"
    if domain == "sites.google.com": domain = "Google Sites"
    if domain == "zenodo.org": domain = "Zenodo"
    return domain
