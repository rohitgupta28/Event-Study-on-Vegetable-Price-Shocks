# Event Study — Vegetable Price Shocks

This repository contains an event-study analysis of convergence around vegetable price shocks across Indian states. It includes data, notebooks, and a main event study script. This README explains how to reproduce results and recommended improvements.

## Structure
- `data/` — input files: `clean_panel.csv`, `halflife_q.xlsx`, `weight.xlsx`
- `notebook/` — analysis notebooks (data cleaning, main event study, summaries)
- `output/event_study_outputs/` — main outputs (CSV + plots + `event_study.py`)

## How to run
1. Create a Python environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Re-run the main event study (optional):

```bash
python output/event_study_outputs/event_study.py --file data/halflife_q.xlsx --sheet Sheet1
```

3. Run robustness checks (adds cluster-robust and Newey-West SEs):

```bash
python robustness_checks.py
```

4. Start Streamlit dashboard (to present results):

```bash
streamlit run streamlit_app.py
```

## Notes & Recommendations
- Reproducibility: add `requirements.txt` (below) and avoid hard-coded absolute paths in `event_study.py`.
- Statistical: include cluster-robust SEs, Newey-West corrections, and sensitivity checks for WINDOW and threshold. See `robustness_checks.py`.
- Interpretation: add a short conclusions section in notebooks summarizing the economic meaning of σ and β changes.
