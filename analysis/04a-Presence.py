"""Reproduces figures and numbers from paper Section 4.1: Artifact Presence.

Builds Figure 3, per-conference artifact presence over time, and runs a
permutation test on presence before vs after each venue's AEC introduction.
"""
from util import get_data, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

# Figure 3: per-conference artifact presence as small multiples.
def artifact_presence_graph(data):
    setup_plot_style()
    years_full = list(range(2000, 2026))
    artifact_percentages = {"Usenix": [], "NDSS": [], "SP": [], "CCS": []}

    for y in years_full:
        year = str(y)[2:]
        if year[0] == "0":
            year = year[1:]

        # Share of that conference/edition's papers where `field` is set.
        def pct(conf, field):
            total = len([d for d in data if d["conference"] == conf and d["edition"] == year])
            if total == 0:
                return 0
            count = len([d for d in data if d["conference"] == conf and d["edition"] == year and d.get(field) is not None])
            return count / total

        artifact_percentages["Usenix"].append(pct("usenix", "discovered_artifact"))
        artifact_percentages["NDSS"].append(pct("ndss", "discovered_artifact"))
        artifact_percentages["SP"].append(pct("sp", "discovered_artifact"))
        artifact_percentages["CCS"].append(pct("ccs", "discovered_artifact"))

    fig, axes = plt.subplots(1, 4, figsize=(20, 4))

    # USENIX
    axes[0].plot(years_full, artifact_percentages["Usenix"], marker="o", label="Artifacts", color="red")
    axes[0].set_title("SEC")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Papers with artifact")
    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[0].axvline(x=2019.5, color="red", linestyle="--", label="AE Introduced")
    axes[0].set_xticks([2000, 2005, 2010, 2015, 2020, 2025])
    axes[0].set_xticklabels(["2000", "2005", "2010", "2015", "2020", "2025"])
    axes[0].set_ylim(0, 1)
    
    # NDSS
    axes[1].plot(years_full, artifact_percentages["NDSS"], marker="o", label="Artifacts", color="#24366e")
    axes[1].set_title("NDSS")
    axes[1].set_xlabel("Year")
    axes[1].yaxis.set_major_formatter(PercentFormatter(1))
    axes[1].axvline(x=2023.5, color="red", linestyle="--", label="AE Introduced")
    axes[1].set_xticks([2000, 2005, 2010, 2015, 2020, 2025])
    axes[1].set_xticklabels(["2000", "2005", "2010", "2015", "2020", "2025"])
    axes[1].set_ylim(0, 1)

    # S&P
    axes[2].plot(years_full, artifact_percentages["SP"], marker="o", label="Artifacts", color="green")
    axes[2].set_title("S&P")
    axes[2].set_xlabel("Year")
    axes[2].yaxis.set_major_formatter(PercentFormatter(1))
    axes[2].set_xticks([2000, 2005, 2010, 2015, 2020, 2025])
    axes[2].set_xticklabels(["2000", "2005", "2010", "2015", "2020", "2025"])
    axes[2].set_ylim(0, 1)
    
    # CCS 
    axes[3].plot(years_full, artifact_percentages["CCS"], marker="o", label="Artifacts", color="purple")
    axes[3].set_title("CCS")
    axes[3].set_xlabel("Year")
    axes[3].yaxis.set_major_formatter(PercentFormatter(1))
    axes[3].axvline(x=2022.5, color="red", linestyle="--", label="AE Introduced")
    axes[3].set_xticks([2000, 2005, 2010, 2015, 2020, 2025])
    axes[3].set_xticklabels(["2000", "2005", "2010", "2015", "2020", "2025"])
    axes[3].set_ylim(0, 1)

    save_plot(fig, "figures/3-artifact_presence_smallmultiples.png")


# Permutation test: does artifact presence rise after AEC introduction? derived from [40]
def olszewski_analysis(data):
    # Mapping conference to its specific AEC introduction year (edition format)
    cutoffs = {
        "usenix": 20,
        "ccs": 23,
        "ndss": 24
    }
    
    before_aec = []
    after_aec = []

    # Fetch relevant fields
    papers = [d for d in data if d.get("conference") in cutoffs and d.get("edition") is not None]

    for paper in papers:
        conf = paper.get("conference", "").lower()
        if conf not in cutoffs:
            continue
            
        try:
            year_val = int(paper.get("edition", 0))
        except ValueError:
            continue

        # 1 if code exists and is not null, 0 otherwise
        has_code = 1 if paper.get("discovered_artifact") else 0
        
        # Split based on specific conference cutoff
        if year_val < cutoffs[conf]:
            before_aec.append(has_code)
        else:
            after_aec.append(has_code)
            

    group_a = np.array(before_aec)
    group_b = np.array(after_aec)
    iterations = 100000
    obs_diff = np.mean(group_b) - np.mean(group_a)
    combined = np.concatenate([group_a, group_b])
    n1 = len(group_a)
    
    # Simulating permutations
    extreme_count = 0
    for _ in range(iterations):
        np.random.shuffle(combined)
        perm_diff = np.mean(combined[n1:]) - np.mean(combined[:n1])
        if perm_diff >= obs_diff:
            extreme_count += 1
    diff = obs_diff
    p_value = extreme_count / iterations
    log_result(f"Observed Difference: {diff:.4f}")
    log_result(f"P-Value: {p_value == 0}")
    log_result("Result: " + ("Accept H0" if p_value > 0.05 else "Reject H0"))
            
    return obs_diff, extreme_count / iterations

if __name__ == "__main__":
    data = get_data()
    artifact_presence_graph(data)
    olszewski_analysis(data)
