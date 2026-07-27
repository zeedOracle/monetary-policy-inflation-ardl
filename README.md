# 🇳🇬 Nigeria Inflation Dashboard

An interactive dashboard that visualizes historical Nigerian inflation data and
generates a short-term forecast using an ARIMA time-series model.

Built to demonstrate: data pipeline → economic modeling → interactive
visualization → deployment.

**[Live demo →](#)** *https://nigeria-inflation-dashboard-dpzrf6uxwt4bf9jqltujuf.streamlit.app/*

## What it does

- Pulls annual inflation data (consumer prices, % change) for Nigeria from the
  [World Bank Open Data API](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG)
- Fits an ARIMA model on the historical series
- Forecasts inflation for the next N years (adjustable in the sidebar)
- Displays everything in an interactive Streamlit dashboard

## Tech stack

- **Python** — data pipeline and modeling
- **pandas** — data wrangling
- **statsmodels** — ARIMA forecasting
- **Streamlit** — dashboard UI
- **Plotly** — interactive charting

## Project structure

```
econometrics-project/
├── data/
│   ├── fetch_data.py     # pulls data from World Bank API
│   └── inflation.csv     # generated after running fetch_data.py
├── app.py                # Streamlit dashboard
├── model.py              # ARIMA forecasting logic
├── requirements.txt
└── README.md
```

## Running it locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/nigeria-inflation-dashboard.git
cd nigeria-inflation-dashboard

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Fetch the data
python data/fetch_data.py

# 5. Run the dashboard
streamlit run app.py
```

## Roadmap / possible extensions

- Swap in NBS monthly CPI data for finer-grained forecasts (World Bank data
  is annual only)
- Add exogenous variables (exchange rate, oil price) to the model
- Compare ARIMA vs Prophet vs SARIMA forecasts side-by-side
- Add a "what-if" scenario slider (e.g. shock exchange rate, see projected impact)

## Data source

World Bank Open Data — Nigeria, Inflation, consumer prices (annual %),
indicator `FP.CPI.TOTL.ZG`.

## Author

Built by [Your Name] — economist working at the intersection of economic
theory and applied data science.
