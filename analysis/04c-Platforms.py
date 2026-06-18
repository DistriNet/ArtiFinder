from util import get_data, domain_colors, domain_hatch, convert_url_to_domain, setup_plot_style, save_plot, log_result
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from urllib.parse import urlparse

#Figure 5: Hosting platform
def domain_area_chart_perct(data):
    setup_plot_style(font_size=18)
    years = list(range(2000, 2026))
    domains = {}
    total_counts = {year:0 for year in years}
    for doc in [d for d in data if d.get("discovered_artifact") is not None and d.get("conference") in ["usenix", "ndss", "sp", "ccs"]]:
        if not doc["discovered_artifact"]: continue
        total_counts[int(doc["edition"])+2000] += 1
        
        artifacts = [link for link in doc["links"] if link.get("score", 0) >= 20]
        artifacts = list(set(["https://" + link["link"] if not urlparse(link["link"]).scheme else link["link"] for link in artifacts]))
        arti_domains = set([convert_url_to_domain(artifact) for artifact in artifacts])
        for domain in arti_domains:
            if domain not in domains:
                domains[domain] = [0] * len(years)
            if 0 <= int(doc["edition"]) <= 25:
                domains[domain][int(doc["edition"])] += 1

    # delete domains that have a total of less than 15 artifacts and store them in other
    other = [0] * len(years)
    edu = [0] * len(years)
    for domain in list(domains.keys()):
        if sum(domains[domain]) < 15:
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
                
    if "Zenodo" in domains: # Forces Zenodo on top of the stack
            zenodo = domains["Zenodo"]
            del domains["Zenodo"]
            domains["Zenodo"] = zenodo
            
    bottom = [0] * len(years)
    fig, ax = plt.subplots(figsize=(10, 6))
    for domain in domains:
        ax.bar(years, domains[domain], bottom=bottom, label=domain, color=domain_colors.get(domain, "#333333"), hatch=domain_hatch.get(domain, ""))
        for i in range(len(years)):
            bottom[i] += domains[domain][i]

    # Ensures "Other" to be the last entry in the legend
    handles, labels = ax.get_legend_handles_labels()
    if "Other" in labels:
        other_index = labels.index("Other")
        handles.append(handles.pop(other_index))
        labels.append(labels.pop(other_index))

    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    ax.set_ylim(0, 1.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("Hosting service")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(handles, labels, loc='upper left', ncol=2, fontsize=13, bbox_to_anchor=(0.0, 1.01))
    ax.set_xticks(range(2000, 2026, 5))
    ax.set_xticklabels([str(year) for year in range(2000, 2026, 5)])
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
    
    save_plot(fig, "figures/5-artifact_domains_perct.png")
    log_result(f"Papers using Zenodo in 2025: {domains['Zenodo'][25] * 100:.2f}%")
    log_result(f"Papers using GitHub in 2025: {domains['GitHub Repo'][25] * 100:.2f}%")
    
# Figure 6: Per conference hosting platform
def domain_area_chart_perct_perconf(data):
    setup_plot_style(font_size=18)
    years = list(range(2000, 2026))
    domain_dicts = {
        "usenix": {},
        "ndss": {},
        "sp": {},
        "ccs": {},
    }
    total_counts = {conf: {year: 0 for year in years} for conf in domain_dicts}
    for doc in [d for d in data if d.get("discovered_artifact") is not None and d.get("conference") in ["usenix", "ndss", "sp", "ccs"]]:
        conf = doc.get("conference", "").lower()
        edition = int(doc.get("edition", -1))
        if conf not in domain_dicts or not doc["discovered_artifact"] or edition > 30 or edition < 0:
            continue
        
        year = edition + 2000
        total_counts[conf][year] += 1
        
        artifacts = [link for link in doc["links"] if link.get("score", 0) >= 20]
        artifacts = ["https://" + link["link"] if not urlparse(link["link"]).scheme else link["link"] for link in artifacts]
        arti_domains = set(convert_url_to_domain(artifact) for artifact in artifacts)
        
        for domain in arti_domains:
            if domain not in domain_dicts[conf]:
                domain_dicts[conf][domain] = [0] * len(years)
            if 0 <= edition <= 25:
                domain_dicts[conf][domain][edition] += 1

    # Filter and group domains
    for conf in domain_dicts:
        domains = domain_dicts[conf]
        other = [0] * len(years)
        edu = [0] * len(years)
        for domain in list(domains.keys()):
            if sum(domains[domain]) < 15 and domain not in domain_colors:
                target = edu if domain.endswith(".edu") else other
                for i in range(len(years)):
                    target[i] += domains[domain][i]
                del domains[domain]
        domains[".edu domains"] = edu
        domains["Other"] = other
        
        # Convert to percentages
        for i, year in enumerate(years):
            total = total_counts[conf][year]
            if total > 0:
                for domain in domains:
                    domains[domain][i] /= total

        if "Zenodo" in domains:
            zenodo = domains["Zenodo"]
            del domains["Zenodo"]
            domains["Zenodo"] = zenodo

    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    confs = ["usenix", "ndss", "sp", "ccs"]
    conf_mapping = {
        "usenix": "SEC",
        "ndss": "NDSS",
        "sp": "S&P",
        "ccs": "CCS"
    }

    for i, conf in enumerate(confs):
        axes[i].set_title(conf_mapping.get(conf, conf.upper()))
        axes[i].set_xlim(years[15] - 0.5, years[-1] + 0.5)
        axes[i].set_ylim(0, 1.55)
        axes[i].yaxis.set_major_formatter(PercentFormatter(1))
        axes[i].set_xlabel("Year")
        if i == 0:
            axes[i].set_ylabel("Hosting service")
        bottom = [0] * len(years)
        domains = domain_dicts[conf]
        
        for domain in domains:
            axes[i].bar(years, domains[domain], bottom=bottom, label=domain, color=domain_colors.get(domain, "#333333"), hatch=domain_hatch.get(domain, ""))
            for j in range(15,len(years)):
                bottom[j] += domains[domain][j]
    axes[0].axvline(x=2019.5, color='red', linestyle='--')
    axes[1].axvline(x=2023.5, color='red', linestyle='--')
    axes[3].axvline(x=2022.5, color='red', linestyle='--')
    
    for i in range(4):
        axes[i].set_xticks([2015, 2020, 2025])
        axes[i].set_xticklabels(["2015", "2020", "2025"])
    
    handles, labels = axes[0].get_legend_handles_labels()
    
    # Ensures "Other" to be the last entry in the legend
    if "Other" in labels:
        other_index = labels.index("Other")
        handles.append(handles.pop(other_index))
        labels.append(labels.pop(other_index))
    
    fig.legend(handles, labels, loc='lower center', ncol=len(handles), fontsize=14, bbox_to_anchor=(0.5, -0.07))
    save_plot(fig, "figures/6-artifact_domains_perct_perconf.png")

# Figure 7: Dedicated domains
def dedicated_domain_graph(data):
    setup_plot_style()
    tld_counts = {}
    conf_counts = {}
    total = {year: 0 for year in range(2000, 2026)}
    counts = {year: {} for year in range(2000, 2026)}
    for doc in [d for d in data if d.get("discovered_artifact") and d.get("conference") in ["usenix", "ndss", "sp", "ccs"]]:
        edition = int(doc.get("edition", -1))
        if 0 <= edition <= 25:
            year = edition + 2000
        if urlparse(doc["discovered_artifact"]["link"]).path in ["", "/"] and doc["discovered_artifact"]["link"].replace("www.", "").count(".") == 1:
            total[year] += 1
            domain = urlparse(doc["discovered_artifact"]["link"]).netloc
            if not domain:
                domain = urlparse("https://" + doc["discovered_artifact"]["link"]).netloc
            tld = domain.split(".")[-1]
            if tld not in tld_counts:
                tld_counts[tld] = 0
            tld_counts[tld] += 1
            if doc["conference"] not in conf_counts:
                conf_counts[doc["conference"]] = 0
            conf_counts[doc["conference"]] += 1
            if tld not in counts[year]:
                counts[year][tld] = 0
            counts[year][tld] += 1

    # filter out tlds that have less than 10 total counts into "other"
    other_tlds = set()
    for tld in list(tld_counts.keys()):
        if tld_counts[tld] < 10:
            other_tlds.add(tld)
            del tld_counts[tld]
    for year in counts:
        for tld in other_tlds:
            if tld in counts[year]:
                if "Other" not in counts[year]:
                    counts[year]["Other"] = 0
                counts[year]["Other"] += counts[year][tld]
                del counts[year][tld]

    fig, ax = plt.subplots(figsize=(10, 5))
    # plot stacked tld per year
    bottom = {year: 0 for year in range(2000, 2026)}
    tlds = set()
    for year in counts:
        for tld in counts[year]:
            tlds.add(tld)
    tlds = sorted(tlds)
    hatches = ["", "//", "\\\\", "xx"]
    for tld in tlds:
        values = []
        for year in range(2000, 2026):
            values.append(counts[year].get(tld, 0))
        ax.bar(range(2000, 2026), values, bottom=[bottom[year] for year in range(2000, 2026)], label='.' + tld if tld != "Other" else "Other", hatch=hatches[tlds.index(tld)])
        for year in range(2000, 2026):
            bottom[year] += counts[year].get(tld, 0)
    
    ax.set_xlabel("Year")
    ax.set_ylabel("Artifacts on dedicated domains")
    ax.legend()
    ax.set_xlim(1999.5, 2025.5)
    
    save_plot(fig, "figures/7-dedicated_domain_graph.png")
    total = sum(sum(year_counts.values()) for year_counts in counts.values())
    log_result(f"Domains using .org TLD: {tld_counts.get('org', 0)/total * 100:.2f}%")
    log_result(f"Domains using .com TLD: {tld_counts.get('com', 0)/total * 100:.2f}%")
    log_result(f"Domains using .net TLD: {tld_counts.get('net', 0)/total * 100:.2f}%")
    log_result(f"Total artifacts on dedicated domains: {total}")

if __name__ == "__main__":
    data = get_data()
    domain_area_chart_perct(data)
    domain_area_chart_perct_perconf(data)
    dedicated_domain_graph(data)
