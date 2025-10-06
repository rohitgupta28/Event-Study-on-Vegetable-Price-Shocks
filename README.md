from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# Define output path
output_path = "/mnt/data/README_Event_Study_Veg_Shocks.pdf"

# Add content
content = """
# 🥦 Event Study on Vegetable Price Shocks

This repository presents an **event-study analysis** of how Indian vegetable prices adjust after major price shocks.  
The project investigates **β- and σ-convergence**, estimates **half-lives of price shocks**, and visualizes results through an interactive **Streamlit dashboard**.

---

## 🎯 Research Motivation & Results

Food price volatility is a key challenge for inflation management in India.  
Vegetables, due to their perishable nature, often drive short-term spikes in inflation.  

This project applies an **event-study framework** to examine convergence and volatility patterns after vegetable price shocks.

**Key Findings:**
- **β-convergence becomes more negative** → faster adjustment after shocks.  
- **Half-life** of shocks falls from ~12 months pre-shock to ~6 months post-shock.  
- **σ-convergence increases** → temporary rise in volatility post-shock.  
- **Cluster and HAC robust SEs** confirm statistical significance.  

📌 **Policy Insight:** Shocks accelerate convergence but amplify short-run volatility — policymakers should stabilize volatility while maintaining long-run market efficiency.

---

## 🗂️ Project Structure

Event Study - Vegetable Shocks/
│
├── data/                           # Raw input data
│   ├── halflife_q.xlsx             # Half-life estimation data
│   ├── weight.xlsx                 # State weights (not used in final version)
│   └── clean_panel.csv             # Cleaned panel dataset
│
├── notebook/                       # Jupyter Notebooks for stepwise analysis
│   ├── 01_data_cleaning.ipynb      # Data cleaning & preprocessing
│   ├── 02_event_study_main.ipynb   # Main event-study analysis
│   ├── 03_shock_summary.ipynb      # Summarizing identified shocks
│   └── 04_cross_shock_analysis.ipynb  # Cross-shock comparative analysis
│
├── output/
│   └── event_study_outputs/        # Model outputs & intermediate results
│       ├──event_study.py          # Script for running event study pipeline
│       ├── beta_convergence_event_path.csv
│       ├── sigma_convergence_event_path.csv
│       ├── shock_dates_used.csv
│       └── robust_se_by_event_time.csv
│
├── streamlit_app.py                # Interactive Streamlit dashboard
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation

---

## 🔄 Workflow  

### Step-by-step process

1. **Data Cleaning (`01_data_cleaning.ipynb`)**  
   - Loads and preprocesses `clean_panel.csv`.  
   - Handles missing values and standardizes time columns.  

2. **Event Identification (`02_event_study_main.ipynb`)**  
   - Detects vegetable price shocks based on volatility thresholds.  
   - Saves `shock_dates_used.csv`.

3. **Convergence Analysis**  
   - Estimates **β-convergence** and **σ-convergence** across states.  
   - Generates `beta_convergence_event_path.csv` and `sigma_convergence_event_path.csv`.

4. **Robustness Checks (`03_shock_summary.ipynb`)**  
   - Tests with **HC1**, **Clustered**, and **HAC** standard errors.  
   - Stores results in `robust_se_by_event_time.csv`.

5. **Cross-Shock Analysis (`04_cross_shock_analysis.ipynb`)**  
   - Compares multiple shocks to study heterogeneity across time.  

6. **Visualization (`streamlit_app.py`)**  
   - Interactive dashboard with:
     - β and σ plots with shock markers  
     - Robustness comparison  
     - Shock timeline visualization  

---

## 🧭 Workflow Diagram

flowchart TD
    A[📦 Data Collection<br/> & Preparation] --> B[🧹 Data Cleaning<br/>(01_data_cleaning.ipynb)]
    B --> C[⚡ Event Identification<br/>(02_event_study_main.ipynb)]
    C --> D[📉 Convergence Analysis<br/>β & σ Estimation]
    D --> E[🧪 Robustness Checks<br/>(03_shock_summary.ipynb)]
    E --> F[🔍 Cross-Shock Comparison<br/>(04_cross_shock_analysis.ipynb)]
    F --> G[📊 Visualization Dashboard<br/>(streamlit_app.py)]

    subgraph Outputs
        H1[beta_convergence_event_path.csv]
        H2[sigma_convergence_event_path.csv]
        H3[robust_se_by_event_time.csv]
        H4[shock_dates_used.csv]
    end

    D --> H1
    D --> H2
    E --> H3
    C --> H4

    G --> I[🎯 Interactive Dashboard<br/>for Policy & Research Insights]


---

## ⚙️ Installation & Setup  

1. Clone the repository:  
   git clone https://github.com/your-username/Event-Study-on-Vegetable-Price-Shocks.git
   cd Event-Study-on-Vegetable-Price-Shocks

2. Create a virtual environment:  
   python -m venv venv
   source venv/bin/activate     # On Windows: venv\\Scripts\\activate

3. Install dependencies:  
   pip install -r requirements.txt

4. Run the event study (optional):  
   python output/event_study_outputs/event_study.py

5. Launch the Streamlit dashboard:  
   streamlit run streamlit_app.py

---

## 🛠️ Tech Stack  

| Category | Tools |
|-----------|--------|
| Language | Python |
| Data Handling | pandas, numpy |
| Statistical Modeling | statsmodels, scikit-learn |
| Visualization | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Documentation | Markdown, Mermaid |

---

## 🧾 Created By  

**Rohit Gupta**  
📧 rohitg2801@gmail.com