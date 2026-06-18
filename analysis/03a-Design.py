from util import get_data, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# 3.1 ArtiFinder Design

# Helper methods to calculate the optimal score cutoff for accuracy
def calc_true_positive(papers, cutoff: int) -> int:
    count = 0
    for p in papers:
        highest_scoring_link = max(p["links"], key=lambda link: link["score"], default=None)
        if highest_scoring_link["score"] < cutoff: highest_scoring_link = None
        if highest_scoring_link and p.get("manual_artifact"):
            count += 1
    return count

def calc_true_negative(papers, cutoff: int) -> int:
    count = 0
    for p in papers:
        highest_scoring_link = max(p["links"], key=lambda link: link["score"], default=None)
        if highest_scoring_link["score"] < cutoff: highest_scoring_link = None
        if not highest_scoring_link and not p.get("manual_artifact"):
            count += 1
    return count

def accuracy(papers, cutoff: int)->float:
    true_positive = calc_true_positive(papers, cutoff)
    true_negative = calc_true_negative(papers, cutoff)
    total = len(papers)
    return ((true_positive + true_negative) / total) if total > 0 else 0

# Creates Figure 2, accuracy in function of the cutoff
def accuracy_plot():
    setup_plot_style()
    data = [p for p in get_data() if p.get("sample")] # only select the sample papers
    for p in data:
        if not p.get("discovered_artifact"):
            p["discovered_artifact"] = max(p["links"], key=lambda link: link["score"], default=None)
    scores = range(0, 105, 5)
    fig, ax = plt.subplots(figsize=(10, 3))
    
    ax.plot(scores, [accuracy(data, i) for i in scores], label="Accuracy")
    ax.set_xlabel("Threshold score")
    ax.set_ylabel("Accuracy")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylim(0.5, 1)
    ax.set_xlim(0, 100)
    
    # Custom ticks as per original logic
    ax.set_yticks(list(ax.get_yticks()) + [0.9124])
    ax.set_yticks([tick for tick in ax.get_yticks() if tick != 0.9])
    
    ax.axvline(x=20, ymin=0, ymax=0.83, color='grey', linestyle='--')
    ax.axhline(y=0.9124, xmin=0, xmax=0.2, color='grey', linestyle='--')
    
    ax.legend()
    save_plot(fig, "figures/2-artifindertool_accuracy.png")

if __name__ == "__main__":
    accuracy_plot()
