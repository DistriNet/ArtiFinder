from util import get_data, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from urllib.parse import urlsplit
from scipy.stats import pointbiserialr
from tabulate import tabulate

# Figure 9
def corr_authors_amount(data):
    setup_plot_style()
    authors_with_artifact = []
    authors_without_artifact = []
    for paper in data:
        author_count = len(paper.get("authors", []))
        if not author_count: continue
        if "discovered_artifact" in paper and paper["discovered_artifact"]:
            authors_with_artifact.append(author_count)
        else:
            authors_without_artifact.append(author_count)
    max_authors = max(max(authors_with_artifact, default=0), max(authors_without_artifact, default=0))
    with_artifact_counts = [0] * (max_authors + 1)
    without_artifact_counts = [0] * (max_authors + 1)
    for count in authors_with_artifact:
        with_artifact_counts[count] += 1
    for count in authors_without_artifact:
        without_artifact_counts[count] += 1
    
    # normalize paper counts to percentage based on total papers with/without artifact
    total_with_artifact = sum(with_artifact_counts)
    total_without_artifact = sum(without_artifact_counts)
    with_artifact_counts = [count / total_with_artifact if total_with_artifact > 0 else 0 for count in with_artifact_counts]
    without_artifact_counts = [count / total_without_artifact if total_without_artifact > 0 else 0 for count in without_artifact_counts]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(max_authors + 1), with_artifact_counts, label="With artifact")
    ax.plot(range(max_authors + 1), without_artifact_counts, label="Without artifact")
    
    ax.set_xlabel("Number of authors")
    ax.set_ylabel("Percentage of papers")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend()
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 0.25)
    ax.set_yticks([i/100 for i in range(0, 21, 5)])
    ax.set_yticklabels([f"{i}%" for i in range(0, 21, 5)])
    
    save_plot(fig, "figures/9-author_count_artifact_correlation.png")
    artifact_presence = [1] * len(authors_with_artifact) + [0] * len(authors_without_artifact)
    author_counts = authors_with_artifact + authors_without_artifact
    correlation, p_value = pointbiserialr(artifact_presence, author_counts)
    log_result(f"Point-biserial correlation: {correlation:.2f}, p-value: {p_value}\n")

# Table 4: Correlation between affiliations and artifact presence
def corr_afill_artifact(data):
    affiliation_stats = {}
    for paper in [d for d in data if d.get("affiliations")]:
        affiliations = paper.get("affiliations", [])
        if not affiliations: continue
        for affiliation in affiliations:
            if affiliation not in affiliation_stats:
                affiliation_stats[affiliation] = {"artifact_count": 0, "total_count": 0, "domains": {}}
            affiliation_stats[affiliation]["total_count"] += 1
            if "discovered_artifact" in paper and paper["discovered_artifact"]:
                affiliation_stats[affiliation]["artifact_count"] += 1
                domain = urlsplit(paper["discovered_artifact"]["link"]).netloc
                if domain not in affiliation_stats[affiliation]["domains"]:
                    affiliation_stats[affiliation]["domains"][domain] = 0
                affiliation_stats[affiliation]["domains"][domain] += 1
    # calculate artifact release ratio
    affiliation_ratios = {aff: stats["artifact_count"] / stats["total_count"] for aff, stats in affiliation_stats.items() if stats["total_count"] > 0}
    log_result("Affiliation Artifact Release Ratios:")
    affiliation_ratios = dict(sorted(affiliation_ratios.items(), key=lambda item: item[1], reverse=True))
    tabulated = []
    for aff, ratio in affiliation_ratios.items():
        if affiliation_stats[aff]['total_count'] >= 50:  # only show affiliations with at least 50 papers
            tabulated.append([
                aff,
                f"{ratio:.2%}",
                affiliation_stats[aff]['total_count'],
                affiliation_stats[aff]['artifact_count']
            ])
    log_result(tabulate(
        tabulated,
        headers=["Affiliation", "Artifact %", "Total Papers", "Artifacts"],
        tablefmt="github"
    ))

if __name__ == "__main__":
    data = get_data()
    corr_authors_amount(data)
    corr_afill_artifact(data)
