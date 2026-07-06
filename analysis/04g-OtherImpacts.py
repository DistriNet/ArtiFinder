"""Reproduces figures and numbers from paper Section 4.7: Popularity metrics.

Runs the citation regressions (overall and AEC-only), builds Figure 10 (average
citations per year by artifact status) and Figure 11 (GitHub stars/forks/watchers
for AE vs non-AE artifacts).
"""
from util import get_data, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pointbiserialr

# 4.7 Citations
def citation_coefficient(rawdata):
    data = []
    for doc in [d for d in rawdata if d.get("citations") is not None]:
        year = int(doc.get("edition", 0))
        citation_count = doc.get("citations", 0)
        has_artifact = 1 if doc.get("discovered_artifact", None) is not None else 0
        
        data.append({"citations": citation_count, "year": year, "artifact": has_artifact})
    log_result(f"{len(data)} papers with citation data")
    df = pd.DataFrame(data)

    correlation, p_value = pointbiserialr(df["artifact"], df["citations"])
    log_result(f"Raw point-biserial correlation: {correlation:.3f} (p={p_value:.3g})")

    X = sm.add_constant(df[["artifact", "year"]])
    y = df["citations"]
    model = sm.OLS(y, X).fit()
    log_result(model.summary())

# 4.7 Citations for AEC compared to non AEC
def citation_coefficient_aec(rawdata):
    data = []
    for doc in [d for d in rawdata if d.get("citations") is not None and d.get("conference") in ["usenix", "ndss"]]:
        year = int(doc.get("edition", 0))
        if doc.get("conference") == "usenix" and year < 20 or year > 30:
            continue
        elif doc.get("conference") == "ndss" and year < 24 or year > 30:
            continue
        citation_count = doc.get("citations", 0)
        has_artifact = 1 if doc.get("secartifacts_artifact", None) is not None else 0
        data.append({"citations": citation_count, "year": year, "artifact": has_artifact})

    df = pd.DataFrame(data)

    correlation, p_value = pointbiserialr(df["artifact"], df["citations"])
    log_result(f"Raw point-biserial correlation: {correlation:.3f} (p={p_value:.3g})")

    X = sm.add_constant(df[["artifact", "year"]])
    y = df["citations"]
    model = sm.OLS(y, X).fit()
    log_result(model.summary())
    
# Figure 10: Citation graph
def citation_graph(data):
    setup_plot_style()
    avg_citation_year_with_artifact = {}
    avg_citation_year_no_artifact = {}
    avg_citation_year_ae = {}
    for year in range(0, 26):
        papers_with_artifact = [d for d in data if d.get("edition") == str(year) and d.get("discovered_artifact") and d.get("citations") is not None]
        papers_no_artifact = [d for d in data if d.get("edition") == str(year) and (not d.get("discovered_artifact")) and d.get("citations") is not None]
        papers_ae = [d for d in data if d.get("edition") == str(year) and d.get("secartifacts_artifact") and d.get("citations") is not None]
        if papers_with_artifact:
            avg_citation_year_with_artifact[year] = sum(p.get("citations", 0) for p in papers_with_artifact) / len(papers_with_artifact)
        else:
            avg_citation_year_with_artifact[year] = 0
        if papers_no_artifact:
            avg_citation_year_no_artifact[year] = sum(p.get("citations", 0) for p in papers_no_artifact) / len(papers_no_artifact)
        else:
            avg_citation_year_no_artifact[year] = 0
        if papers_ae:
            avg_citation_year_ae[year] = sum(p.get("citations", 0) for p in papers_ae) / len(papers_ae)
        else:
            avg_citation_year_ae[year] = None

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(avg_citation_year_with_artifact.keys(), avg_citation_year_with_artifact.values(), label="Papers with artifact")
    ax.plot(avg_citation_year_no_artifact.keys(), avg_citation_year_no_artifact.values(), label="Papers without artifact")
    ax.plot(avg_citation_year_ae.keys(), avg_citation_year_ae.values(), label="Papers with AE-participation")
    
    ax.set_xlabel("Year")
    ax.set_ylabel("Average citation count")
    ax.set_xlim(0, 25)
    ax.set_xticks(range(0, 26, 5))
    ax.set_xticklabels([str(2000 + y) for y in range(0, 26, 5)])
    ax.legend()
    
    save_plot(fig, "figures/10-avg_citation_per_year.png")

# Figure 11: GitHub stats graph
def gh_stats_graph(data):
    setup_plot_style(font_size=14)
    stars_with_ae = {year:0 for year in range(20, 26)}
    stars_without_ae = {year:0 for year in range(20, 26)}
    forks_with_ae = {year:0 for year in range(20, 26)}
    forks_without_ae = {year:0 for year in range(20, 26)}
    watchers_with_ae = {year:0 for year in range(20, 26)}
    watchers_without_ae = {year:0 for year in range(20, 26)}
    totals_with_ae = {year:0 for year in range(20, 26)}
    totals_without_ae = {year:0 for year in range(20, 26)}
    editions=range(20, 26)
    for doc in [d for d in data if d.get("discovered_artifact") and d.get("github_stats") and d.get("edition") in [str(e) for e in editions]]:
        stats = doc.get("github_stats", {}).get("github_stats", None)
        if not "github" in str(doc.get("discovered_artifact", {}).get("link", "")).lower(): continue
        if doc.get("conference") == "sp": continue
        if doc.get("conference") == "ccs" and int(doc.get("edition", 0)) < 23: continue
        if doc.get("conference") == "ndss" and int(doc.get("edition", 0)) < 24: continue
        if stats:
            if doc.get("secartifacts_artifact", None):
                stars_with_ae[ int(doc.get("edition")) ] += stats.get("stars", 0)
                forks_with_ae[ int(doc.get("edition")) ] += stats.get("forks", 0)
                watchers_with_ae[ int(doc.get("edition")) ] += stats.get("watchers", 0)
                totals_with_ae[ int(doc.get("edition")) ] += 1
            else:
                stars_without_ae[ int(doc.get("edition")) ] += stats.get("stars", 0)
                forks_without_ae[ int(doc.get("edition")) ] += stats.get("forks", 0)
                watchers_without_ae[ int(doc.get("edition")) ] += stats.get("watchers", 0)
                totals_without_ae[ int(doc.get("edition")) ] += 1

    # average
    for year in editions:
        if totals_with_ae[year] > 0:
            stars_with_ae[year] /= totals_with_ae[year]
            forks_with_ae[year] /= totals_with_ae[year]
            watchers_with_ae[year] /= totals_with_ae[year]
        if totals_without_ae[year] > 0:
            stars_without_ae[year] /= totals_without_ae[year]
            forks_without_ae[year] /= totals_without_ae[year]
            watchers_without_ae[year] /= totals_without_ae[year]
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 4))

    axes[0].plot(stars_with_ae.keys(), stars_with_ae.values(), label="With AE", marker='o')
    axes[0].plot(stars_without_ae.keys(), stars_without_ae.values(), label="Without AE", marker='o')
    axes[0].set_title("GitHub Stars")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Average Stars")
    
    axes[1].plot(forks_with_ae.keys(), forks_with_ae.values(), label="With AE", marker='o')
    axes[1].plot(forks_without_ae.keys(), forks_without_ae.values(), label="Without AE", marker='o')
    axes[1].set_title("GitHub Forks")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Average Forks")

    axes[2].plot(watchers_with_ae.keys(), watchers_with_ae.values(), label="With AE", marker='o')
    axes[2].plot(watchers_without_ae.keys(), watchers_without_ae.values(), label="Without AE", marker='o')
    axes[2].set_title("GitHub Watchers")
    axes[2].set_xlabel("Year")
    axes[2].set_ylabel("Average Watchers")
    axes[2].set_yticks([0, 5, 10, 15])

    for i in range(3):
        axes[i].set_xticks(range(20, 26))
        axes[i].set_xticklabels([2000 + i for i in range(20, 26)])
        axes[i].legend()
        
    save_plot(fig, "figures/11-gh_stats.png")

if __name__ == "__main__":
    data = get_data()
    citation_coefficient(data)
    citation_coefficient_aec(data)
    citation_graph(data)
    gh_stats_graph(data)
