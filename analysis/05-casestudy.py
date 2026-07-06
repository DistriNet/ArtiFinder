"""Reproduces figures and numbers from paper Section 5: Case Study.

Applies ArtiFinder to the ACSAC dataset: logs its accuracy against the ACSAC
SecArtifacts ground truth and builds Figure 12, ACSAC hosting-platform share
over time.
"""
from urllib.parse import urlparse

from util import get_data_acsac, domain_colors, domain_hatch, convert_url_to_domain, setup_plot_style, save_plot, log_result, url_matches_any_discovered_artifact
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Tally TP/TN/FP/FN (and unlinked misses) for one ground-truth dataset.
def confusion_matrix(data, data_subset):
    counts = {"TP": 0, "TN": 0, "FP": 0, "FN": 0, "TP_docs": [], "not_linked": 0}
    for doc in [d for d in data if d.get(f"accuracy_{data_subset}") is not None]:
        has_disc_artifact = doc.get("discovered_artifact") is not None
        has_actual_artifact = doc.get(f"{data_subset}_artifact") is not None
        if has_disc_artifact and has_actual_artifact:
            counts["TP"] += 1
            counts["TP_docs"].append(doc)
        elif not has_disc_artifact and not has_actual_artifact:
            counts["TN"] += 1
        elif has_disc_artifact and not has_actual_artifact:
            counts["FP"] += 1
        elif not has_disc_artifact and has_actual_artifact:
            counts["FN"] += 1
            if doc.get("not_linked"):
                counts["not_linked"] += 1
    return counts

# Among true positives, split into exact URL matches vs accepted alternates.
def identification_accuracy(data_subset, cm):
    exact = 0
    alt = 0
    for doc in cm["TP_docs"]:
        artifact = doc[f"{data_subset}_artifact"]
        disc_artifacts = [l for l in doc.get("links", []) if l.get("score") >= 20]
        if url_matches_any_discovered_artifact(artifact, disc_artifacts):
            exact += 1
        elif doc[f"accuracy_{data_subset}"] is True:
            alt += 1
    return exact, alt

# Log the accuracy breakdown for the ACSAC SecArtifacts dataset.
def c_matrix(data):
    name = "ACSAC SecArtifacts"
    subset = "secartifacts"

    cm = confusion_matrix(data, subset)
    exact, alt = identification_accuracy(subset, cm)
    total = cm['TP'] + cm['FP'] + cm['FN'] + cm['TN']
    incorrect = cm['TP'] - exact - alt
    missing = cm['not_linked']
    
    log_result(f"Accuracy for {name} dataset: (n={total})")
    log_result(f"  Correct presence: {(exact + alt)/total*100:.1f}% (exact: {exact/total*100:.1f}%, alt: {alt/total*100:.1f}%)")
    log_result(f"  Correct absence: {(cm['TN'] + missing)/total*100:.1f}%, (no link: {cm['TN']/total*100:.1f}%, missing link: {missing/total*100:.1f}%)")
    log_result(f"  Wrong presence: {(cm['FP'] + incorrect)/total*100:.1f}%, (no link: {cm['FP']/total*100:.1f}%, incorrect link: {incorrect/total*100:.1f}%)")
    log_result(f"  Wrong absence: {(cm['FN'] - missing)/total*100:.1f}%")
    log_result(f"  Overall accuracy: {(exact + alt + cm['TN'] + missing)/total*100:.1f}%")


# Figure 12: ACSAC hosting-platform share per year as a stacked bar chart.
def domain_area_chart_perct_acsac(data):
    setup_plot_style()
    years = list(range(2017, 2026))
    domains = {}
    total_counts = {year:0 for year in years}
    for doc in [d for d in data if d.get("discovered_artifact") is not None]:
        if not doc["discovered_artifact"]: continue
        if int(doc["edition"]) > 25:continue
        total_counts[int(doc["edition"])+2000] += 1
        
        artifacts = [link for link in doc["links"] if link.get("score", 0) >= 20]
        artifacts = list(set(["https://" + link["link"] if not urlparse(link["link"]).scheme else link["link"] for link in artifacts]))
        arti_domains = set([convert_url_to_domain(artifact) for artifact in artifacts])
        for domain in arti_domains:
            if domain not in domains:
                domains[domain] = [0] * len(years)
            if 0 <= int(doc["edition"]) <= 26:
                domains[domain][int(doc["edition"]) - 17] += 1
    # delete domains that have a total of less than 15 artifacts and store them in other
    other = [0] * len(years)
    edu = [0] * len(years)
    for domain in list(domains.keys()):
        if sum(domains[domain]) < 15 and domain not in domain_colors:
            if domain.endswith(".edu"):
                for i in range(len(years)):
                    edu[i] += domains[domain][i]
                del domains[domain]
            else:
                for i in range(len(years)):
                    other[i] += domains[domain][i]
                del domains[domain]
    domains[".edu domains"] = edu
    domains["Other"] = other
    for i in range(len(years)):
        total = total_counts[years[i]]
        if total > 0:
            for domain in domains:
                domains[domain][i] = domains[domain][i] / total
    if "Zenodo" in domains:
        zenodo = domains["Zenodo"]
        del domains["Zenodo"]
        domains["Zenodo"] = zenodo
    bottom = [0] * len(years)
    
    fig, ax = plt.subplots(figsize=(7, 5.5))
    
    for domain in domains:
        ax.bar(years, domains[domain], bottom=bottom, label=domain, color=domain_colors.get(domain, "#333333"), hatch=domain_hatch.get(domain, None))
        for i in range(len(years)):
            bottom[i] += domains[domain][i]
    # Ensures "Other" to be the last entry in the legend
    handles, labels = ax.get_legend_handles_labels()
    if "Other" in labels:
        other_index = labels.index("Other")
        handles.append(handles.pop(other_index))
        labels.append(labels.pop(other_index))
    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    ax.set_ylim(0, 1.5)
    ax.set_xlabel("Year")
    ax.set_ylabel("Hosting service")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(handles, labels, loc='upper right', ncol=3, fontsize=12)
    ax.set_xticks(list(range(2017, 2026, 2)))
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
    
    save_plot(fig, "figures/12-artifact_domains_perct_acsac.png")
    
if __name__ == "__main__":
    data = get_data_acsac()
    c_matrix(data)
    domain_area_chart_perct_acsac(data)