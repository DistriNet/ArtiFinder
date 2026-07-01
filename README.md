# ArtiFinder

ArtiFinder is an automated tool for discovering and ranking research artifacts linked from the PDFs of papers. It extracts every URL from a paper, then scores each candidate through a multi-phase ranking pipeline to identify the link most likely to be the paper's artifact.

This repository contains the artifact for the USENIX Security 2026 paper:

> **"Not all those who share are lost: Analyzing 25 Years of Cybersecurity Artifact Sharing Practices Through Automated Discovery"**

It contains three things:

1. **`artifinder/`** — the ArtiFinder package (the tool itself).
2. **`artifinder-cli.py`** — a command-line front-end that runs ArtiFinder on a single paper PDF.
3. **`data/` + `analysis/` + `reproduce_results.py`** — the datasets and scripts that reproduce every figure and table in the paper.

*Due to copyright law, we only publish the metadata for each analysed paper.*

A snapshot of the code and data used for the paper is available at [Zenodo](https://doi.org/10.5281/zenodo.20412202).

We invite corrections and updates to our dataset at [GitHub](github.com/DistriNet/ArtiFinder-data).

## Dependencies

### Python

ArtiFinder requires **Python 3.12 or newer**.

### System packages

In order to parse PDFs, ArtiFinder uses [Poppler](https://poppler.freedesktop.org/).

On a Debian-based system, all necessary packages can be installed as follows:

```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libxml2 cmake pkg-config libcairo2-dev libpoppler-glib-dev gir1.2-poppler-0.18 girepository-2.0 libgirepository1.0-dev
```


### Python packages

Python dependencies are managed through pip.
We encourage the use of a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
The installation can be verified by running `python test_install.py`.

### Optional: GitHub token

One heuristic (`Created`) queries the GitHub API to check a repository's creation date. In order to prevent rate-limits from the GitHub API, you can create a token and add it to `.env`. A token can be created in your [GitHub profile](https://github.com/settings/personal-access-tokens).

```bash
cp .env.example .env
# edit .env and set GITHUB_TOKEN=<your personal access token>
```
---

## Running ArtiFinder on a single paper

`artifinder-cli.py` takes a paper PDF (plus optional metadata) and prints the ranked candidate links and the single discovered artifact, if any.

```bash
python artifinder-cli.py --pdf path/to/paper.pdf \
    --title "Not all those who share are lost" \
    --authors "Daan Vansteenhuyse, Arthur Bols, Lieven Desmet, Victor Le Pochat, Jo Van Bulck, Marton Bognar" \
    --year 2026 \
    --conf usenix
```

Options:

| Flag | Description |
|------|-------------|
| `--pdf` | **Required.** Path to the paper PDF. |
| `--title` | Paper title (improves title-match scoring). |
| `--authors` | Comma-separated author list. |
| `--year` | Publication year (enables the repo-age check). |
| `--conf` | Conference name (`usenix`, `ccs`, `ndss`, `sp`). |
| `--json` | Path to a JSON file with the metadata above; CLI flags override its fields. |
| `-o, --output` | Write the result JSON to a file instead of stdout. |
| `-v, --verbose` | Debug-level logging. |
| `-q, --quiet` | Errors only. |

The output JSON contains the paper metadata, every candidate `link` with its score, and `discovered_artifact` — the top-ranked link (set only when its score clears the confidence threshold of 20).

Metadata can also be supplied entirely from a file:

```bash
python artifinder-cli.py --pdf paper.pdf --json paper-meta.json -o result.json
```

---

## Reproducing the paper's analysis

`reproduce_results.py` runs the analysis scripts in `analysis/`, writes the output to `results.md`, and writes plots to `figures/`. It reads the bundled datasets in `data/`.

Create the output directory and run the full reproduction:

```bash
mkdir -p figures
python reproduce_results.py
```

This regenerates `results.md` and all `figures/*.png`

Reproduce a single paper section:

```bash
python reproduce_results.py --section 4.1     # Section 4.1: Artifact Presence
```

Reproduce a grouped experiment from our artifact appendix:

```bash
python reproduce_results.py --experiment E2
```

## Datasets

- `data/data.json` — the full longitudinal dataset (USENIX Security, NDSS, IEEE S&P, ACM CCS,
  2000–2025), with paper metadata and ArtiFinder's discovered links.
- `data/data-acsac.json` — the ACSAC dataset used for the Section 5 case study.
- `data/by_conference/` — a human-readable per-conference/per-year YAML view.
