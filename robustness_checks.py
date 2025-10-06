#!/usr/bin/env python3
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

PROJ = Path(".")
DATA = PROJ / "data" / "clean_panel.csv"
OUT = PROJ / "output" / "event_study_outputs"
OUT.mkdir(parents=True, exist_ok=True)

# Parameters (match event_study.py defaults)
WINDOW = 6
REL_COL = "relc"
STATE_COL = "State"
DATE_COL = "Date"

def robust_month_diff(a, b):
    return (a.year - b.year) * 12 + (a.month - b.month)

# Load data
df = pd.read_csv(DATA, parse_dates=[DATE_COL])
df = df.rename(columns={DATE_COL: "date"})
df["date"] = pd.to_datetime(df["date"])

# Load shocks
shocks_file = OUT / "shock_dates_used.csv"
if not shocks_file.exists():
    raise FileNotFoundError("shock_dates_used.csv not found. Run event_study.py first.")
shocks = pd.read_csv(shocks_file)
# shock_date column is YYYY-MM; parse using to_datetime with format
shocks["shock_date"] = pd.to_datetime(shocks["shock_date"], format="%Y-%m")
shock_dates = shocks["shock_date"].unique().tolist()

# Build event windows same as event_study.py
frames = []
for sdate in shock_dates:
    sdate = pd.to_datetime(sdate)
    lo = sdate - pd.DateOffset(months=WINDOW)
    hi = sdate + pd.DateOffset(months=WINDOW)
    sub = df.loc[(df["date"] >= lo) & (df["date"] <= hi), [STATE_COL, "date", REL_COL]].copy()
    if sub.empty:
        continue
    sub["shock_date"] = sdate
    sub["event_time"] = sub["date"].apply(lambda d: robust_month_diff(d, sdate))
    frames.append(sub)

event_df = pd.concat(frames, ignore_index=True).sort_values([STATE_COL, "shock_date", "date"]).reset_index(drop=True)

# compute d_rel and lag_rel per state-shock group
event_df["d_rel"] = event_df.groupby([STATE_COL, "shock_date"])[REL_COL].diff()
event_df["lag_rel"] = event_df.groupby([STATE_COL, "shock_date"])[REL_COL].shift(1)

# For each event_time, run three regressions: HC1 (original), cluster by state, Newey-West (HAC)
rows = []
for tau, g in event_df.groupby("event_time"):
    gg = g.dropna(subset=["lag_rel", "d_rel"])
    n = len(gg)
    if n < 30:
        rows.append({"event_time": int(tau), "n_obs": n,
                     "beta_hc1": np.nan, "se_hc1": np.nan,
                     "beta_cluster": np.nan, "se_cluster": np.nan,
                     "beta_hac": np.nan, "se_hac": np.nan})
        continue
    X = sm.add_constant(gg["lag_rel"])
    y = gg["d_rel"]

    # HC1 (as original)
    m_hc1 = sm.OLS(y, X, missing="drop").fit(cov_type="HC1")
    b_hc1 = m_hc1.params.get("lag_rel", np.nan)
    se_hc1 = m_hc1.bse.get("lag_rel", np.nan)

    # Cluster robust by state
    try:
        m_cl = sm.OLS(y, X, missing="drop").fit(cov_type="cluster", cov_kwds={"groups": gg[STATE_COL]})
        b_cl = m_cl.params.get("lag_rel", np.nan)
        se_cl = m_cl.bse.get("lag_rel", np.nan)
    except Exception as e:
        b_cl, se_cl = np.nan, np.nan

    # Newey-West HAC (use lag=1 by default for monthly data)
    try:
        m_hac = sm.OLS(y, X, missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags":1})
        b_hac = m_hac.params.get("lag_rel", np.nan)
        se_hac = m_hac.bse.get("lag_rel", np.nan)
    except Exception as e:
        b_hac, se_hac = np.nan, np.nan

    rows.append({"event_time": int(tau), "n_obs": n,
                 "beta_hc1": float(b_hc1), "se_hc1": float(se_hc1),
                 "beta_cluster": float(b_cl), "se_cluster": float(se_cl),
                 "beta_hac": float(b_hac), "se_hac": float(se_hac)})

outdf = pd.DataFrame(rows).sort_values("event_time")
outdf.to_csv(OUT / "robust_se_by_event_time.csv", index=False)
print("Saved robust_se_by_event_time.csv to", OUT)
