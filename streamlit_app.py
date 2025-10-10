# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------
# CONFIG & SETUP
# -------------------
st.set_page_config(
    page_title="Event Study – Vegetable Price Shocks",
    page_icon="🥕",
    layout="wide",
)

DATA_DIR = "output/event_study_outputs"

# Load data safely
def load_csv(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

beta_df = load_csv("beta_convergence_event_path.csv")
sigma_df = load_csv("sigma_convergence_event_path.csv")
robust_df = load_csv("robust_se_by_event_time.csv")
shock_df = load_csv("shock_dates_used.csv")

# -------------------
# SIDEBAR
# -------------------
st.sidebar.title("📊 About this Project")
st.sidebar.info(""" 
*Event Study: Vegetable Price Shocks in India*  

- Studies convergence dynamics after price shocks  
- Uses β-convergence & σ-convergence methods  
- Provides robustness checks (Cluster, HAC)  
- Interactive dashboard for exploration  
""")
st.sidebar.markdown("[📄 View README](README.md)")

# -------------------
# HEADER
# -------------------
st.title("🥦 Event Study on Vegetable Price Shocks")
st.markdown("An interactive research dashboard for analyzing **price-shock convergence** and **robustness checks**.")

# -------------------
# NAVIGATION TABS
# -------------------
tabs = st.tabs(["📘 Overview", "📈 Analysis", "🛠 Robustness", "📊 Sensitivity", "✅ Conclusion"])

# -------------------
# TAB 1: OVERVIEW
# -------------------
with tabs[0]:
    st.subheader("Abstract")
    st.write("""
    This project investigates how Indian vegetable markets respond to price shocks.  
    We analyze convergence dynamics using β-convergence and σ-convergence,  
    estimate half-life of shocks, and test robustness with clustered & HAC errors.  
    """)

    with st.expander("Key Findings", expanded=True):
        st.markdown("""
        - **β becomes more negative after shocks** → faster convergence.  
        - **Half-life falls** from ~12 months pre-shock to ~6 months post-shock.  
        - **σ rises** → higher short-run volatility after shocks.  
        - **Cluster-robust SEs** confirm significance of β around event months.  
        """)

    with st.expander("Glossary"):
        st.markdown("""
        - **β-convergence**: measures speed of adjustment after shocks.  
        - **σ-convergence**: measures volatility/dispersion across states.  
        - **Half-life**: time taken for half the shock effect to dissipate.  
        - **HC1 / Cluster / HAC**: different standard error estimators.  
        """)

# -------------------
# TAB 2: ANALYSIS
# -------------------
with tabs[1]:
    st.subheader("Analysis of β and σ over Event Time")

    # Prepare shock dates
    shock_dates = []
    if not shock_df.empty:
        shock_df['shock_date'] = pd.to_datetime(shock_df['shock_date'], format="%Y-%m")
        shock_dates = shock_df['shock_date'].tolist()

    # --- β-convergence plot ---
    if not beta_df.empty:
        fig = px.line(beta_df, x="event_time", y="beta", markers=True, title="β-convergence Path")

        # Add vertical shock lines + labels
        for sdate in shock_dates:
            fig.add_vline(x=sdate, line_width=1, line_dash="dash", line_color="red")
            fig.add_annotation(
                x=sdate, y=max(beta_df['beta']), text=sdate.strftime("%Y-%m"),
                showarrow=True, arrowhead=1, yshift=20, font=dict(color="red", size=10)
            )

        st.plotly_chart(fig, use_container_width=True)

    # --- σ-convergence plot ---
    if not sigma_df.empty:
        fig2 = px.line(
            sigma_df, 
            x="event_time", 
            y="avg_sigma", 
            markers=True, 
            title="σ-convergence Path"
        )

        for sdate in shock_dates:
            fig2.add_vline(x=sdate, line_width=1, line_dash="dash", line_color="red")
            fig2.add_annotation(
                x=sdate, y=max(sigma_df['avg_sigma']), text=sdate.strftime("%Y-%m"),
                showarrow=True, arrowhead=1, yshift=20, font=dict(color="red", size=10)
            )

        st.plotly_chart(fig2, use_container_width=True)

    # --- Shock timeline (standalone scatter) ---
    if not shock_df.empty:
        st.subheader("Shock Timeline by State")
        fig_state = px.scatter(
            shock_df,
            x="shock_date",
            y="state",             # state on y-axis
            color="state",         # optional: color by state
            hover_data=["shock_date"], 
            title="State-wise Shock Dates"
    )
    st.plotly_chart(fig_state, use_container_width=True)

# -------------------
# TAB 3: ROBUSTNESS
# -------------------
with tabs[2]:
    st.subheader("Robustness Checks (HC1 vs Cluster vs HAC)")

    if not robust_df.empty:
        # Dropdown to select SE type
        se_type = st.radio("Select SE Type:", ["HC1", "Cluster", "HAC"], horizontal=True)

        if se_type == "HC1":
            y, se = "beta_hc1", "se_hc1"
        elif se_type == "Cluster":
            y, se = "beta_cluster", "se_cluster"
        else:
            y, se = "beta_hac", "se_hac"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=robust_df["event_time"], y=robust_df[y],
            mode="lines+markers", name="β estimates"
        ))
        fig.add_trace(go.Scatter(
            x=robust_df["event_time"],
            y=robust_df[y] + 1.96*robust_df[se],
            mode="lines", line=dict(dash="dash"), name="Upper 95% CI"
        ))
        fig.add_trace(go.Scatter(
            x=robust_df["event_time"],
            y=robust_df[y] - 1.96*robust_df[se],
            mode="lines", line=dict(dash="dash"), name="Lower 95% CI"
        ))
        fig.update_layout(title=f"β with {se_type} SEs")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View Robustness Data Table"):
            st.dataframe(robust_df)

        st.download_button("📥 Download Robustness Results (CSV)",
                           robust_df.to_csv(index=False).encode("utf-8"),
                           file_name="robust_se_by_event_time.csv")

# -------------------
# TAB 4: SENSITIVITY
# -------------------
with tabs[3]:
    st.subheader("Sensitivity Analysis (Window & Threshold)")

    st.write("⚠️ Placeholder: run multiple `event_study.py` with varying parameters and store results as CSVs for comparison.")
    st.write("Suggested grid: window = [3, 6, 12], threshold = [1.0, 1.5, 2.0].")

    # TODO: Load precomputed sensitivity CSV if available
    st.info("Once you generate sensitivity_grid.csv, we’ll add interactive side-by-side plots here.")

# -------------------
# TAB 5: CONCLUSION
# -------------------
with tabs[4]:
    st.subheader("Conclusion & Policy Implications")
    st.write("""
    - Price shocks accelerate convergence across Indian states but at the cost of higher volatility.  
    - Policymakers should consider interventions to stabilize short-term volatility while allowing long-term convergence.  
    - Robustness checks confirm the statistical significance of β convergence results.  
    """)
    st.markdown("---")
    st.markdown("**Prepared by:** Rohit Gupta.")
