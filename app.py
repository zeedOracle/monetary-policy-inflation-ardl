"""
app.py
Nigeria Inflation Dashboard — Streamlit app.

Run locally with:
    streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px

from model import forecast_inflation

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "inflation.csv")

st.set_page_config(page_title="Nigeria Inflation Dashboard", layout="wide")

st.title("🇳🇬 Nigeria Inflation Dashboard")
st.caption("Historical inflation (World Bank, annual %) with a short-term ARIMA forecast.")


@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    return pd.read_csv(DATA_PATH)


df = load_data()

if df is None:
    st.error(
        "No data found. Run `python data/fetch_data.py` first to download the dataset, "
        "then refresh this page."
    )
    st.stop()

# --- Sidebar controls ---
st.sidebar.header("Controls")
years_back = st.sidebar.slider("Years of history to show", 5, len(df), min(20, len(df)))
forecast_periods = st.sidebar.slider("Years to forecast", 1, 10, 5)

filtered_df = df.tail(years_back).reset_index(drop=True)

# --- Forecast ---
combined = forecast_inflation(filtered_df, periods=forecast_periods)

# --- Chart ---
fig = px.line(
    combined,
    x="year",
    y="inflation_rate",
    color="type",
    markers=True,
    title="Inflation Rate: Historical vs Forecast",
    labels={"inflation_rate": "Inflation Rate (%)", "year": "Year"},
)
st.plotly_chart(fig, use_container_width=True)

# --- Key stats ---
col1, col2, col3 = st.columns(3)
latest = df.iloc[-1]
col1.metric("Latest recorded year", int(latest["year"]))
col2.metric("Latest inflation rate", f"{latest['inflation_rate']:.2f}%")
forecast_only = combined[combined["type"] == "forecast"]
if not forecast_only.empty:
    col3.metric(
        f"Forecast for {int(forecast_only.iloc[-1]['year'])}",
        f"{forecast_only.iloc[-1]['inflation_rate']:.2f}%",
    )

# --- Raw data ---
with st.expander("View raw data"):
    st.dataframe(df, use_container_width=True)

st.caption("Data source: World Bank Open Data (indicator FP.CPI.TOTL.ZG). Model: ARIMA — for demonstration, not investment advice.")
