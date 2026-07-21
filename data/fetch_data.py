"""
fetch_data.py
Pulls Nigeria inflation data (Consumer Prices, annual %) from the World Bank API
and saves it as a clean CSV for the dashboard to use.

World Bank indicator used: FP.CPI.TOTL.ZG (Inflation, consumer prices, annual %)
Docs: https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG

Run this whenever you want to refresh the data:
    python data/fetch_data.py
"""

import requests
import pandas as pd
import os

COUNTRY_CODE = "NGA"          # Nigeria
INDICATOR = "FP.CPI.TOTL.ZG"  # Inflation, consumer prices (annual %)
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "inflation.csv")


def fetch_worldbank_indicator(country: str, indicator: str, per_page: int = 200) -> pd.DataFrame:
    """Fetch a World Bank indicator for a given country and return a tidy DataFrame."""
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {"format": "json", "per_page": per_page}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if len(payload) < 2 or payload[1] is None:
        raise ValueError("No data returned from World Bank API. Check the indicator/country code.")

    records = payload[1]
    df = pd.DataFrame(records)

    # Keep only what we need, drop rows with no value (years without data yet)
    df = df[["date", "value"]].dropna(subset=["value"])
    df = df.rename(columns={"date": "year", "value": "inflation_rate"})
    df["year"] = df["year"].astype(int)
    df = df.sort_values("year").reset_index(drop=True)

    return df


def main():
    print(f"Fetching {INDICATOR} for {COUNTRY_CODE}...")
    df = fetch_worldbank_indicator(COUNTRY_CODE, INDICATOR)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")
    print(df.tail())


if __name__ == "__main__":
    main()
