"""Reproduces figures and numbers from paper Section 4.4: Long-term artifact availability.

Builds Figure 8, the share of unreachable artifacts per year split into GitHub
vs other hosts, and logs the fraction of GitHub artifacts with no content.
"""
from util import get_data, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Figure 8: Availability
def unreachable_domains(data):
    setup_plot_style()
    # graph for unreachable domains, percentage of unreachable domains per year and difference between github and others
    other_stats_per_year = {year:0 for year in range(2000, 2026)}
    gh_stats_per_year = {year:0 for year in range(2000, 2026)}
    for doc in [d for d in data if d.get("discovered_artifact")]:
        year = doc.get("edition", "unknown")
        if int(year) > 26: continue
        year = int(year) + 2000
        if not doc.get("unreachable", False): continue
        if 'github.com' in doc["discovered_artifact"]["link"]:
            gh_stats_per_year[year] += 1
        else:
            other_stats_per_year[year] += 1

    # percentage per year
    for year in other_stats_per_year:
        total = len([d for d in data if d.get("edition") == str(year - 2000) and d.get("discovered_artifact")])
        if total > 0:
            other_stats_per_year[year] = other_stats_per_year[year] / total
            gh_stats_per_year[year] = gh_stats_per_year[year] / total
        else:
            other_stats_per_year[year] = 0
            gh_stats_per_year[year] = 0

    fig, ax = plt.subplots(figsize=(10, 5))
    # stacked bar chart
    ax.bar(other_stats_per_year.keys(), other_stats_per_year.values(), label='Other', color="#7f7f7f", hatch="//")
    ax.bar(gh_stats_per_year.keys(), gh_stats_per_year.values(), label='GitHub Repo', color="#1f77b4", bottom=list(other_stats_per_year.values()))
    # Ensures "Other" to be the last entry in the legend
    handles, labels = ax.get_legend_handles_labels()
    if "Other" in labels:
        other_index = labels.index("Other")
        handles.append(handles.pop(other_index))
        labels.append(labels.pop(other_index))
    ax.set_xlabel("Year")
    ax.set_ylabel("Unreachable artifacts")
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xlim(2005.5, 2025.5)
    ax.set_xticks(list(range(2006, 2026, 4)))
    ax.set_ylim(0, 0.26)
    ax.set_yticks([0, 0.05, 0.1, 0.15, 0.2, 0.25])
    ax.legend(handles, labels)
    
    save_plot(fig, "figures/8-artifact_reachability_by_year.png")

if __name__ == "__main__":
    data = get_data()
    unreachable_domains(data)
    singlefile_gh = len([d for d in data if d.get("discovered_artifact") and 'github.com' in d["discovered_artifact"]["link"] and d.get("singlefile")])
    gh_total = len([d for d in data if d.get("discovered_artifact") and 'github.com' in d["discovered_artifact"]["link"]])
    log_result(f"Percentage of GitHub artifacts without content: {singlefile_gh / gh_total * 100:.2f}%" if gh_total > 0 else "No GitHub artifacts found.")
