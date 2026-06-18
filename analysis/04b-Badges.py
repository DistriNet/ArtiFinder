from util import get_data, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

#Figure 4: Badge evolution over the years for ndss and usenix
def badges_evolution(data):
    years = range(20, 26)
    badge_counts = {"UsenixArtifact": [0] * len(years), "NDSSArtifact": [0] * len(years), "UsenixArtifactBadge.AVAILABLE": [0] * len(years), "UsenixArtifactBadge.PASSED": [0] * len(years), "UsenixArtifactBadge.FUNCTIONAL": [0] * len(years), "UsenixArtifactBadge.REPRODUCED": [0] * len(years), "NDSSArtifactBadge.AVAILABLE": [0] * len(years), "NDSSArtifactBadge.FUNCTIONAL": [0] * len(years), "NDSSArtifactBadge.REPRODUCED": [0] * len(years), "Usenix": [0] * len(years), "NDSS": [0] * len(years)}
    for year in years:
        badge_counts["NDSS"][year - 20] = len([d for d in data if d.get("conference") == "ndss" and d.get("edition") == str(year)])
        badge_counts["Usenix"][year - 20] = len([d for d in data if d.get("conference") == "usenix" and d.get("edition") == str(year)])
        badge_counts["UsenixArtifact"][year - 20] = len([d for d in data if d.get("conference") == "usenix" and d.get("edition") == str(year) and d.get("discovered_artifact")])
        badge_counts["NDSSArtifact"][year - 20] = len([d for d in data if d.get("conference") == "ndss" and d.get("edition") == str(year) and d.get("discovered_artifact")])
        
        for doc in [d for d in data if d.get("conference") in ["usenix", "ndss"] and d.get("edition") == str(year)]:
            if "badges" in doc and doc["badges"]:
                if doc["conference"] == "usenix":
                    if "UsenixArtifactBadge.AVAILABLE" in doc["badges"]:
                        badge_counts["UsenixArtifactBadge.AVAILABLE"][year - 20] += 1
                    if "UsenixArtifactBadge.FUNCTIONAL" in doc["badges"]:
                        badge_counts["UsenixArtifactBadge.FUNCTIONAL"][year - 20] += 1
                    if "UsenixArtifactBadge.REPRODUCED" in doc["badges"]:
                        badge_counts["UsenixArtifactBadge.REPRODUCED"][year - 20] += 1
                    if "UsenixArtifactBadge.PASSED" in doc["badges"]:
                        badge_counts["UsenixArtifactBadge.PASSED"][year - 20] += 1
                elif doc["conference"] == "ndss":
                    if "NDSSArtifactBadge.AVAILABLE" in doc["badges"]:
                        badge_counts["NDSSArtifactBadge.AVAILABLE"][year - 20] += 1
                    if "NDSSArtifactBadge.FUNCTIONAL" in doc["badges"]:
                        badge_counts["NDSSArtifactBadge.FUNCTIONAL"][year - 20] += 1
                    if "NDSSArtifactBadge.REPRODUCED" in doc["badges"]:
                        badge_counts["NDSSArtifactBadge.REPRODUCED"][year - 20] += 1
                        
    # percentages per year
    badge_counts["NDSSArtifactBadge.AVAILABLE"] = [count / badge_counts["NDSS"][i] if badge_counts["NDSS"][i] > 0 else 0 for i, count in enumerate(badge_counts["NDSSArtifactBadge.AVAILABLE"])]
    badge_counts["NDSSArtifactBadge.FUNCTIONAL"] = [count / badge_counts["NDSS"][i] if badge_counts["NDSS"][i] > 0 else 0 for i, count in enumerate(badge_counts["NDSSArtifactBadge.FUNCTIONAL"])]
    badge_counts["NDSSArtifactBadge.REPRODUCED"] = [count / badge_counts["NDSS"][i] if badge_counts["NDSS"][i] > 0 else 0 for i, count in enumerate(badge_counts["NDSSArtifactBadge.REPRODUCED"])]
    badge_counts["UsenixArtifactBadge.AVAILABLE"] = [count / badge_counts["Usenix"][i] if badge_counts["Usenix"][i] > 0 else 0 for i, count in enumerate(badge_counts["UsenixArtifactBadge.AVAILABLE"])]
    badge_counts["UsenixArtifactBadge.FUNCTIONAL"] = [count / badge_counts["Usenix"][i] if badge_counts["Usenix"][i] > 0 else 0 for i, count in enumerate(badge_counts["UsenixArtifactBadge.FUNCTIONAL"])]
    badge_counts["UsenixArtifactBadge.REPRODUCED"] = [count / badge_counts["Usenix"][i] if badge_counts["Usenix"][i] > 0 else 0 for i, count in enumerate(badge_counts["UsenixArtifactBadge.REPRODUCED"])]
    badge_counts["UsenixArtifactBadge.PASSED"] = [count / badge_counts["Usenix"][i] if badge_counts["Usenix"][i] > 0 else 0 for i, count in enumerate(badge_counts["UsenixArtifactBadge.PASSED"])]
    badge_counts["NDSSArtifact"] = [count / badge_counts["NDSS"][i] if badge_counts["NDSS"][i] > 0 else 0 for i, count in enumerate(badge_counts["NDSSArtifact"])]
    badge_counts["UsenixArtifact"] = [count / badge_counts["Usenix"][i] if badge_counts["Usenix"][i] > 0 else 0 for i, count in enumerate(badge_counts["UsenixArtifact"])]
    bar_width = 0.1
    
    x = [year for year in years]
    setup_plot_style(font_size=18)
    plt.xlabel("Year")
    plt.ylim(0, 1)
    plt.xticks(x, ["20" +str(year) for year in years])
    plt.subplots_adjust(left=0.06, right=0.98,  bottom=0.12, wspace=0.2)
    fig, axes = plt.subplots(1, 2, figsize=(20, 6.3 ))
    axes[0].bar([i for i in x], badge_counts["UsenixArtifactBadge.PASSED"], width=bar_width, label="Passed", color="#ffb3b3")
    axes[0].bar([i - 1 *bar_width for i in x], badge_counts["UsenixArtifactBadge.AVAILABLE"], width=bar_width, label="Available", color="#ff9999")
    axes[0].bar([i for i in x], badge_counts["UsenixArtifactBadge.FUNCTIONAL"], width=bar_width, label="Functional", color="#ff4d4d")
    axes[0].bar([i + bar_width for i in x], badge_counts["UsenixArtifactBadge.REPRODUCED"], width=bar_width, label="Reproduced", color="#cc0000")
    axes[1].bar([i - bar_width for i in x], badge_counts["NDSSArtifactBadge.AVAILABLE"], width=bar_width, label="Available", color="#99ccff")
    axes[1].bar([i for i in x], badge_counts["NDSSArtifactBadge.FUNCTIONAL"], width=bar_width, label="Functional", color="#4da6ff")
    axes[1].bar([i + bar_width for i in x], badge_counts["NDSSArtifactBadge.REPRODUCED"], width=bar_width, label="Reproduced", color="#0066cc")
    axes[0].plot([i for i in x], badge_counts["UsenixArtifact"], marker='o', color='red', label="Total detected artifacts" )
    axes[1].plot([i for i in x], badge_counts["NDSSArtifact"], marker='o', color='#24366e', label="Total detected artifacts" )

    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[1].yaxis.set_major_formatter(PercentFormatter(1))
    axes[0].set_title("SEC")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Share of papers")
    axes[0].set_xticks(x, ["20" +str(year) for year in years])
    axes[0].set_ylim(0, 1)
    axes[0].legend(loc="upper left", fontsize="small")
    
    axes[1].set_title("NDSS")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Share of papers")
    axes[1].set_xticks(x, ["20" +str(year) for year in years])
    axes[1].set_ylim(0, 1)
    axes[1].legend(loc="upper left", fontsize="small")
    
    plt.savefig("figures/4-badges_evolution_multiples.png")
    plt.close()

if __name__ == "__main__":
    data = get_data()
    badges_evolution(data)
