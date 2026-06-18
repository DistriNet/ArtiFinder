import argparse
import subprocess
import sys
import os

RESULTS_FILE = "results.md"

def run_script(script_name, section_title):
    print(f"--- Running {script_name} ---")
    script_path = os.path.join("analysis", script_name)
    
    with open(RESULTS_FILE, "a") as f:
        f.write(f"## {section_title}\n\n")

    result = subprocess.run([sys.executable, script_path], capture_output=False, text=True)
    if result.returncode != 0:
        print(f"Error running {script_name}")
    
    with open(RESULTS_FILE, "a") as f:
        f.write("\n")
        
    print(f"--- Finished {script_name} ---\n")

def main():
    parser = argparse.ArgumentParser(description="Reproduce ArtiFinder USENIX 2026 results.")
    parser.add_argument("--section", type=str, choices=["all", "1", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "5"],
                        default="all", help="Section to reproduce (default: all)")
    parser.add_argument("--experiment", type=str, choices=["E2", "E3"], help="Specific experiment to reproduce (optional)")
    
    args = parser.parse_args()

    mapping = {
        "1": ("01-introduction.py", "Section 1: Introduction"),
        "3.1": ("03a-Design.py", "Section 3.1: ArtiFinder Design"),
        "3.2": ("03b-Accuracy.py", "Section 3.2: ArtiFinder Accuracy"),
        "3.3": ("03c-Ablation.py", "Section 3.3: Ablation Study"),
        "4.1": ("04a-Presence.py", "Section 4.1: Artifact Presence"),
        "4.2": ("04b-Badges.py", "Section 4.2: Artifact Badges"),
        "4.3": ("04c-Platforms.py", "Section 4.3: Artifact Platforms"),
        "4.4": ("04d-Availability.py", "Section 4.4: Artifact Availability"),
        "4.5": ("04e-Topics.py", "Section 4.5: Artifact Topics"),
        "4.6": ("04f-Authors.py", "Section 4.6: Artifact Authors"),
        "4.7": ("04g-OtherImpacts.py", "Section 4.7: Other Impacts"),
        "5": ("05-casestudy.py", "Section 5: Case Study"),
    }

    with open(RESULTS_FILE, "w") as f:
        f.write("# ArtiFinder USENIX 2026 Reproduction Results\n\n")

    experiment_mapping = {
        "E2": ["3.1", "3.2", "3.3"],
        "E3": ["1", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "5"]
    }

    if args.experiment:
        sections_to_run = experiment_mapping[args.experiment]
    elif args.section == "all":
        sections_to_run = ["1", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "5"]
    else:
        sections_to_run = [args.section]

    for section in sections_to_run:
        script, title = mapping[section]
        run_script(script, title)

if __name__ == "__main__":
    main()
