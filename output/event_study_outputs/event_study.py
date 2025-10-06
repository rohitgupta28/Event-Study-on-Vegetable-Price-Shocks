
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
# USER CONFIG (default fallback)
# =========================
# If user doesn't provide via CLI, use this:
INPUT_XLSX = args.file if args.file else r"C:\Users\rohit\Downloads\halflife_q.xlsx"
SHEET_NAME = args.sheet

EXPLICIT_SHOCKS = []  # specify shock months like ["2013-09","2019-09"] or leave empty for auto-detect
OUTDIR = Path("event_study_outputs")
WINDOW = 6
THRESH_STD_MULTIPLIER = 1.5
REL_PRIORITY = ["relc", "relu", "relr"]

# =========================
# Utility helpers
# =========================
def build_date(df, year_col="year", month_col="month"):
    month_map = {
        "january":1, "february":2, "march":3, "april":4, "may":5, "june":6,
        "july":7, "august":8, "september":9, "october":10, "november":11, "december":12
    }
    m = df[month_col].astype(str).str.strip().str.lower().map(month_map).fillna(df[month_col])
    m = m.astype(int)
    y = df[year_col].astype(int)
    return pd.to_datetime(dict(year=y, month=m, day=1))


def detect_columns(df):
    cols = [c.lower().strip() for c in df.columns]
    df.columns = cols
    state_col = next((c for c in ["state","state_name","statename","st_name","states"] if c in cols), None)
    year_col  = "year"  if "year"  in cols else None
    month_col = "month" if "month" in cols else None
    date_col  = "date"  if "date"  in cols else None
    rel_col = next((c for c in REL_PRIORITY if c in cols), None)
    if rel_col is None:
        for c in cols:
            if c.startswith("rel") and pd.api.types.is_numeric_dtype(df[c]):
                rel_col = c
                break
    veg_cols = [c for c in cols if ("veg" in c) or ("vegetable" in c) or ("vegetables" in c)]
    return state_col, year_col, month_col, date_col, rel_col, veg_cols


def robust_month_diff(a, b):
    return (a.year - b.year) * 12 + (a.month - b.month)


def ensure_outdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# =========================
# Main pipeline
# =========================
def main():
    # 1) Read Excel
    path = Path(INPUT_XLSX)
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {INPUT_XLSX}")

    xl = pd.ExcelFile(path)
    if SHEET_NAME not in xl.sheet_names:
        raise ValueError(f"Sheet '{SHEET_NAME}' not found. Available: {xl.sheet_names}")

    df = xl.parse(SHEET_NAME)
    state_col, year_col, month_col, date_col, rel_col, veg_cols = detect_columns(df)

    if state_col is None:
        for c in df.columns:
            if df[c].dtype == "O" and 28 <= df[c].nunique() <= 40:
                state_col = c
                break
    if state_col is None:
        raise ValueError("Couldn't detect the state column. Please rename to 'state' (or similar).")

    # 2) Date handling
    if date_col is None:
        if (year_col is None) or (month_col is None):
            raise ValueError("Need either a 'date' column or ('year' + 'month') columns.")
        df["date"] = build_date(df, year_col, month_col)
        date_col = "date"
    else:
        df["date"] = pd.to_datetime(df[date_col])

    # 3) Convergence variable
    if rel_col is None:
        candidates = [c for c in df.columns if c not in [state_col, date_col, year_col, month_col] and pd.api.types.is_numeric_dtype(df[c])]
        if not candidates:
            raise ValueError("No numeric series found for convergence analysis.")
        rel_col = candidates[0]

    keep_cols = [state_col, "date", rel_col]
    for v in veg_cols:
        if v not in keep_cols:
            keep_cols.append(v)
    panel = df[keep_cols].copy()
    panel = panel.dropna(subset=[state_col, "date", rel_col])
    panel = panel.sort_values([state_col, "date"]).reset_index(drop=True)

    # 4) Detect shocks
    if EXPLICIT_SHOCKS:
        shock_dates = pd.to_datetime(pd.Series(EXPLICIT_SHOCKS) + "-01").dt.to_period("M").dt.to_timestamp()
        shock_source = "User-specified shock months"
    else:
        if veg_cols:
            chosen = veg_cols[0]
            nat_veg = panel.groupby("date")[chosen].mean()
            veg_mom = nat_veg.pct_change()
            thr = veg_mom.mean() + THRESH_STD_MULTIPLIER * veg_mom.std()
            shock_dates = veg_mom[veg_mom > thr].index.to_list()
            shock_source = f"Vegetables series '{chosen}' (mean + {THRESH_STD_MULTIPLIER}*std MoM)"
        else:
            panel["d_rel"] = panel.groupby(state_col)[rel_col].diff()
            abs_change = panel.groupby("date")["d_rel"].apply(lambda s: np.nanmean(np.abs(s)))
            thr = abs_change.mean() + THRESH_STD_MULTIPLIER * abs_change.std()
            shock_dates = abs_change[abs_change > thr].index.to_list()
            shock_source = f"Proxy on cross-state Δ{rel_col} (mean + {THRESH_STD_MULTIPLIER}*std)"

        if len(shock_dates) > 24:
            series_for_rank = (veg_mom if veg_cols else abs_change).loc[shock_dates]
            shock_dates = list(series_for_rank.sort_values(ascending=False).head(24).index)

    if not shock_dates:
        raise RuntimeError("No shock months detected. Consider setting EXPLICIT_SHOCKS or lowering the threshold.")

    # 5) Build event windows
    frames = []
    for sdate in shock_dates:
        lo = sdate - pd.DateOffset(months=WINDOW)
        hi = sdate + pd.DateOffset(months=WINDOW)
        sub = panel.loc[(panel["date"] >= lo) & (panel["date"] <= hi), [state_col, "date", rel_col]].copy()
        if sub.empty:
            continue
        sub["shock_date"] = sdate
        sub["event_time"] = sub["date"].apply(lambda d: robust_month_diff(d, sdate))
        frames.append(sub)

    if not frames:
        raise RuntimeError("No event windows constructed. Check your date range and shocks.")

    event_df = pd.concat(frames, ignore_index=True)
    event_df = event_df.sort_values([state_col, "shock_date", "date"]).reset_index(drop=True)

    # 6) σ-convergence
    sigmas = (event_df
              .groupby(["shock_date", "event_time"])[rel_col]
              .agg(lambda x: np.nanstd(x, ddof=1))
              .reset_index())
    sigma_path = sigmas.groupby("event_time")[rel_col].mean().reset_index().rename(columns={rel_col: "avg_sigma"})

    # 7) β-convergence
    event_df["lag_rel"] = event_df.groupby([state_col, "shock_date"])[rel_col].shift(1)
    event_df["d_rel"]   = event_df.groupby([state_col, "shock_date"])[rel_col].diff()

    rows = []
    for tau, g in event_df.groupby("event_time"):
        gg = g.dropna(subset=["lag_rel", "d_rel"])
        if len(gg) >= 30:
            X = sm.add_constant(gg["lag_rel"])
            y = gg["d_rel"]
            model = sm.OLS(y, X, missing="drop").fit(cov_type="HC1")
            beta = model.params.get("lag_rel", np.nan)
            se   = model.bse.get("lag_rel", np.nan)
            hl = np.nan
            if (beta is not None) and (-1 < beta < 0):
                try:
                    hl = np.log(0.5) / np.log(1 + beta)
                except Exception:
                    hl = np.nan
            rows.append({"event_time": int(tau), "beta": float(beta), "se": float(se),
                         "half_life_months": float(hl) if pd.notna(hl) else np.nan, "n": int(len(gg))})

    beta_path = pd.DataFrame(rows).sort_values("event_time")

    # 8) Save outputs
    ensure_outdir(OUTDIR)
    sigma_path.to_csv(OUTDIR / "sigma_convergence_event_path.csv", index=False)
    beta_path.to_csv(OUTDIR / "beta_convergence_event_path.csv", index=False)
    pd.DataFrame({"shock_date": pd.to_datetime(shock_dates).strftime("%Y-%m")}).to_csv(OUTDIR / "shock_dates_used.csv", index=False)

    # ✅ FIX: Use UTF-8 for writing summary
    with open(OUTDIR / "summary.txt", "w", encoding="utf-8") as f:
        f.write(f"States: {event_df[state_col].nunique()}\n")
        f.write(f"Convergence variable: {rel_col}\n")
        f.write(f"Shock source: {shock_source}\n")
        f.write(f"Num shocks: {len(shock_dates)}\n")
        f.write(f"Window: ±{WINDOW} months\n")

    # 9) Plots
    plt.figure()
    plt.plot(sigma_path["event_time"], sigma_path["avg_sigma"], marker="o")
    plt.axvline(0, linestyle="--")
    plt.xlabel("Event time (months)")
    plt.ylabel("Avg cross-sectional std (σ)")
    plt.title("σ-convergence around shocks")
    plt.tight_layout()
    plt.savefig(OUTDIR / "sigma_convergence_event_path.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(beta_path["event_time"], beta_path["beta"], marker="o")
    plt.axhline(0, linestyle="--")
    plt.axvline(0, linestyle="--")
    plt.xlabel("Event time (months)")
    plt.ylabel("Beta estimate")
    plt.title("β-convergence around shocks")
    plt.tight_layout()
    plt.savefig(OUTDIR / "beta_convergence_event_path.png", dpi=160)
    plt.close()

    valid_hl = beta_path.dropna(subset=["half_life_months"])
    if not valid_hl.empty:
        plt.figure()
        plt.plot(valid_hl["event_time"], valid_hl["half_life_months"], marker="o")
        plt.axvline(0, linestyle="--")
        plt.xlabel("Event time (months)")
        plt.ylabel("Half-life (months)")
        plt.title("Implied half-life by event time")
        plt.tight_layout()
        plt.savefig(OUTDIR / "half_life_by_event_time.png", dpi=160)
        plt.close()

    print("=== Event Study Complete ===")
    print(f"Convergence variable: {rel_col}")
    print(f"Shock source: {shock_source}")
    print(f"Shocks used: {len(shock_dates)} → saved to {OUTDIR/'shock_dates_used.csv'}")
    print(f"σ-path → {OUTDIR/'sigma_convergence_event_path.csv'}")
    print(f"β-path → {OUTDIR/'beta_convergence_event_path.csv'}")
    print(f"Charts → {OUTDIR}")


if __name__ == "__main__":
    main()
