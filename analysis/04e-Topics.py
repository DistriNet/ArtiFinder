"""Reproduces figures and numbers from paper Section 4.5: Artifact by paper topic.

Builds Table 4, artifact-release rates per paper topic (topics with >=100 papers), sorted by artifact percentage.
"""
from util import get_data, log_result
from tabulate import tabulate

# Table 4: topics
def topic_stats(data):
    topic_counts = {}
    for doc in [d for d in data if d.get("paper_topic")]:
        topic = doc.get("paper_topic")
        if topic not in topic_counts:
            topic_counts[topic] = {"with_artifact": 0, "without_artifact": 0}
        if doc.get("discovered_artifact"):
            topic_counts[topic]["with_artifact"] += 1
        else:
            topic_counts[topic]["without_artifact"] += 1
    tabulated = []
    discarded_topics = []
    for topic, counts in topic_counts.items():
        total = counts["with_artifact"] + counts["without_artifact"]
        if total >= 100:
            tabulated.append([
                topic,
                counts["with_artifact"],
                counts["without_artifact"],
                total,
                f"{(counts['with_artifact']/total)*100:.2f}%",
            ])
        else:
            discarded_topics.append((topic, total))
    tabulated.sort(key=lambda x: x[4], reverse=True)
    log_result(tabulate(
        tabulated,
        headers=["Topic", "With Artifact", "Without Artifact", "Total Papers", "Artifact %"],
        tablefmt="github"
    ))

if __name__ == "__main__":
    data = get_data()
    topic_stats(data)
