"""Reproduces figures and numbers from paper Section 3.3: ArtiFinder Accuracy.

Compares ArtiFinder's discovered artifacts against the SecArtifacts, GetIn and
manual-sample ground-truth datasets and logs presence/absence accuracy per set.
"""
from util import get_data, url_matches_any_discovered_artifact, log_result

# Section 3.2: accuracy compared to Manual, Get In and SecArtifacts datasets

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

# Log the full accuracy breakdown for each ground-truth dataset.
def c_matrix(data):
    datasets = [
        ("SecArtifacts", "secartifacts"),
        ("GetIn", "getin"),
        ("Manual Sample", "sample"),
    ]
    
    for name, subset in datasets:
        cm = confusion_matrix(data, subset)
        exact, alt = identification_accuracy(subset, cm)
        total = cm['TP'] + cm['FP'] + cm['FN'] + cm['TN']
        incorrect = cm['TP'] - exact - alt
        missing = cm['not_linked']
        if total == 0:
            continue
        
        log_result(f"Accuracy for {name} dataset: (n={total})")
        log_result(f"  Correct presence: {(exact + alt)/total*100:.1f}% (exact: {exact/total*100:.1f}%, alt: {alt/total*100:.1f}%)")
        log_result(f"  Correct absence: {(cm['TN'] + missing)/total*100:.1f}%, (no link: {cm['TN']/total*100:.1f}%, missing link: {missing/total*100:.1f}%)")
        log_result(f"  Wrong presence: {(cm['FP'] + incorrect)/total*100:.1f}%, (no link: {cm['FP']/total*100:.1f}%, incorrect link: {incorrect/total*100:.1f}%)")
        log_result(f"  Wrong absence: {(cm['FN'] - missing)/total*100:.1f}%")
        log_result(f"  Overall accuracy: {(exact + alt + cm['TN'] + missing)/total*100:.1f}%")

if __name__ == "__main__":
    data = get_data()
    c_matrix(data)