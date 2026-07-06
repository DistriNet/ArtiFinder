"""Reproduces figures and numbers from paper Section 1: Introduction.

Builds Figure 1, the aggregate share of papers with a discovered artifact per
year across all conferences, and logs the 2000 vs 2025 endpoints.
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from util import get_data, setup_plot_style, save_plot, log_result

# Figure 1: Aggregate artifact presence over the years
def agg_presence_graph():
    setup_plot_style(font_size=15)
    years = list(range(2000, 2026))
    counts = {year: 0 for year in years}
    totals = {year: 0 for year in years}
    data = get_data()
    for paper in data:
        year = int(paper["edition"]) + 2000
        totals[year] += 1
        if paper.get("discovered_artifact") is not None:
            counts[year] += 1
    percentages = [counts[year] / totals[year] if totals[year] > 0 else 0 for year in years]
    fig, ax = plt.subplots(figsize=(10, 4))
    
    ax.plot(years, percentages, marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Papers with artifact")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlim(1999.5, 2025.5)
    ax.set_ylim(0, 0.85)
    
    save_plot(fig, "figures/1-artifact_presence_agg.png")
    log_result("Artifact presence over the years:")
    for year, percentage in zip(years, percentages):
        if year in [2000, 2025]:
            log_result(f"{year}: {percentage:.2%}")
    
if __name__ == "__main__":
    agg_presence_graph()