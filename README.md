## Event Study on Vegetable Price Shocks

This project analyzes the impact of vegetable price shocks on macroeconomic stability in India using an event-study methodology. The analysis estimates how quickly shocks converge (half-life) and provides interactive visualizations via a Streamlit dashboard.

## Features

- Event-study framework for identifying and analyzing price shocks

- Estimation of shock convergence (half-life)

- Interactive Streamlit dashboard for timelines and shock visualizations

- Modular and reproducible Python code

## Project Structure

Event Study - Vegetable Shocks/

│

├── data/                           # Raw input data

│   ├── halflife_q.xlsx             # Half-life estimation data

│   ├── weight.xlsx                 # State weights 

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

│       └── event_study.py          # Script for running event study pipeline

│       ├── beta_convergence_event_path.csv

│       ├── sigma_convergence_event_path.csv

│       ├── shock_dates_used.csv

│       ├── robust_se_by_event_time.csv

│

├── streamlit_app.py                # Interactive Streamlit dashboard

├── requirements.txt                # Python dependencies

└── README.md                       # Project documentation

## Installation

- Clone this repository:

  git clone https://github.com/your-username/veg-shock-event-study.git

  cd veg-shock-event-study


- Create and activate a virtual environment:

  python -m venv venv
  
  source venv/bin/activate   # On Windows: venv\Scripts\activate


- Install dependencies:

  pip install -r requirements.txt

## Usage

- Run the event study analysis:

  python event_study.py

- Launch the Streamlit dashboard:

  streamlit run streamlit_app.py              #Open the app in your browser (usually http://localhost:8501).

## Tech Stack

- Python (pandas, numpy, statsmodels, scikit-learn)

- Streamlit (for dashboard)

- Plotly (for interactive plots)


## Created by

Rohit Gupta.
