import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

# =========================
# CLI Argument Parser
# =========================
parser = argparse.ArgumentParser(description="Event-study on convergence around vegetable-price shock periods")
parser.add_argument("--file", type=str, help="Path to the Excel file")
parser.add_argument("--sheet", type=str, default="Sheet1", help="Sheet name (default: Sheet1)")
args = parser.parse_args()

# =========================
# USER CONFIG
# =========================
INPUT_XLSX = args.file if args.file else r"C:\Users\rohit\Desktop\Rohit\Event Study - Vegetable Shocks\data\halflife_q.xlsx"
SHEET_NAME = args.sheet
WEIGHT_PATH = Path(r"C:\Users\rohit\Desktop\Rohit\Event Study - Vegetable Shocks\data\weight.xlsx")

OUTDIR = Path(r"C:\Users\rohit\Desktop\Rohit\Event Study - Vegetable Shocks\output\event_study_outputs")
OUTDIR.mkdir(parents=True, exist_ok=True)

WINDOW = 6
THRESH_STD_MULTIPLIER = 1.5

# =========================
# Helper Functions
# =========================
def build_date(df, year_col="year", month_col="month"):
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    m = df[month_col].astype(str).str.strip().str.lower().map(month_map).fillna(df[month_col])
    m = m.astype(int)
    y = df[year_col].astype(int)
    return pd.to_datetime(dict(year=y, month=m, day=1))

def robust_month_diff(a, b):
    return (a.year - b.year) * 12 + (a.month - b.month)

def ensure_outdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# =========================
# Main Analysis
# =========================
def main():
    print("=== Running Event Study with State-level Shocks ===")

    # 1. Load main data
    df = pd.read_excel(INPUT_XLSX, sheet_name=SHEET_NAME)
    df.columns = [c.strip().lower() for c in df.columns]
    if "state" not in df.columns:
        raise ValueError("Expected a 'state' column in input data")

    # 2. Build date if not present
    if "date" not in df.columns:
        df["date"] = build_date(df)
    df["date"] = pd.to_datetime(df["date"])
    rel_col = next((c for c in df.columns if c.startswith("rel") or "price" in c), None)
    if rel_col is None:
        raise ValueError("No relevant numeric column found for analysis")

    # 3. Load weight matrix
    if WEIGHT_PATH.exists():
        w_df = pd.read_excel(WEIGHT_PATH)
        w_df = w_df.rename(columns={"Unnamed: 0": "state"})
        w_df = w_df.set_index("state")
        w_df.columns = [c.strip() for c in w_df.columns]
        print(f"Loaded weight matrix with shape {w_df.shape}")
    else:
        raise FileNotFoundError("weight.xlsx not found")

    # 4. Detect per-state shocks
    shocks = []
    for state, grp in df.groupby("state"):
        grp = grp.sort_values("date")
        grp["mom"] = grp[rel_col].pct_change()
        mean, std = grp["mom"].mean(), grp["mom"].std()
        threshold = mean + THRESH_STD_MULTIPLIER * std
        detected = grp.loc[grp["mom"] > threshold, "date"].dt.to_period("M").dt.to_timestamp()
        for d in detected:
            shocks.append({"state": state, "shock_date": d})
    shock_df = pd.DataFrame(shocks)
    print(f"Detected {len(shock_df)} shocks across {shock_df['state'].nunique()} states")

    # 5. Propagate shocks via weights
    propagated = []
    for _, row in shock_df.iterrows():
        src = row["state"]
        sdate = row["shock_date"]
        if src not in w_df.index:
            continue
        affected = w_df.loc[src]
        for target, weight in affected.items():
            if weight > 0:
                propagated.append({"shock_date": sdate.strftime("%Y-%m"), 
                                   "source_state": src,
                                   "state": target,
                                   "weight_value": weight})

    shock_propagated_df = pd.DataFrame(propagated)
    shock_propagated_df.to_csv(OUTDIR / "shock_dates_used.csv", index=False)
    print(f"Saved detailed shock mapping → {OUTDIR / 'shock_dates_used.csv'}")

    # 6. Save summary
    with open(OUTDIR / "summary.txt", "w", encoding="utf-8") as f:
        f.write(f"Total shocks detected: {len(shock_df)}\n")
        f.write(f"States affected: {shock_df['state'].nunique()}\n")
        f.write(f"Total propagated records: {len(shock_propagated_df)}\n")
        f.write(f"Weight matrix shape: {w_df.shape}\n")

    print("✅ State-level shock detection completed successfully.")


if __name__ == "__main__":
    main()
