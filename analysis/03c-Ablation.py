"""Reproduces figures and numbers from paper Section 3.4: Ablation Study.

Removes individual scoring heuristics, re-derives the discovered artifact, and
logs how SecArtifacts accuracy drops without each heuristic.
"""
from util import get_data, log_result

# Section 3.3: Ablation study on heuristics

# Strip one heuristic from every link, rescore, and re-pick the top artifact.
def filter_heuristic(papers: list[dict], heuristic: str) -> list[dict]:
    filtered = []
    count = 0
    for p in papers:
        if "discovered_artifact" in p and p["discovered_artifact"] and heuristic in (b.get("name") for b in p["discovered_artifact"].get("breakdown", [])):
            count += 1
        if not p.get("links"): 
            filtered.append(p)
            continue
        new_links = []
        for link in p["links"]:
            new_breakdown = [b for b in link.get("breakdown", []) if b.get("name") != heuristic]
            new_score = sum(b.get("value", 0) for b in new_breakdown)
            new_link = {**link, "breakdown": new_breakdown, "score": new_score}
            new_links.append(new_link)
        p["links"] = new_links
        p["new_discovered_artifact"] = max(new_links, key=lambda link: link["score"], default=None)
        if p["new_discovered_artifact"]["score"] < 20: 
            p["new_discovered_artifact"] = None
        filtered.append(p)
    log_result(f"Filtered {count} occurrences of heuristic {heuristic}")
    log_result(f"percentage of links affected: {round(count / len(papers) * 100, 2)}%")
    return filtered

# Run the ablation for each heuristic and log the resulting accuracy.
def ablation_study():
    data = get_data()
    data = [d for d in data if d.get("accuracy_secartifacts") is not None and d.get("not_linked") is None]
    secartifacts_total = len(data)
    heuristics = ["LocationInPaper", "GithubRepo"]
    for heuristic in heuristics:
        log_result(f"Ablation study for heuristic: {heuristic}")
        filtered_papers = filter_heuristic(data, heuristic)
        secartifacts_correct = 0
        for paper in filtered_papers:
            if bool(paper.get("discovered_artifact")) ^ bool(paper.get("new_discovered_artifact")): continue
            if paper.get("accuracy_secartifacts") and (paper.get("new_discovered_artifact") == paper.get("discovered_artifact") or paper["discovered_artifact"]["link"] == paper["new_discovered_artifact"]["link"]):
                secartifacts_correct += 1
        log_result(f"SecArtifacts accuracy without {heuristic}: {round(secartifacts_correct / secartifacts_total * 100, 2)}%")
        log_result("-----")

if __name__ == "__main__":
    ablation_study()
