"""
fetch_data.py
Pulls the 5 variables used in the ARDL model (INFL, INT, EXC, MS, FDI) for
Nigeria from the World Bank API and merges them into one CSV.

IMPORTANT CAVEAT: This is NOT the exact dataset used in the original thesis
(which was sourced from CBN Statistical Bulletin / CBN annual reports).
World Bank series are a different vintage and sometimes a different precise
definition (e.g. lending rate vs. monetary policy rate). Treat this as a
transparent, reproducible companion dataset, not a byte-for-byte replication
of the original numbers. This distinction is deliberately kept visible
throughout the dashboard rather than smoothed over.

Run with:
    python data/fetch_data.py
"""

import requests
import pandas as pd
import os

COUNTRY_CODE = "NGA"
START_YEAR = 1960
END_YEAR = 2025

# World Bank indicator codes for each model variable
INDICATORS = {
    "INFL": "FP.CPI.TOTL.ZG",        # Inflation, consumer prices (annual %)
    "INT": "FR.INR.LEND",            # Lending interest rate (%)
    "EXC": "PA.NUS.FCRF",            # Official exchange rate (NGN per US$, period average)
    "MS": "FM.LBL.BMNY.CN",          # Broad money (current LCU)
    "FDI": "BX.KLT.DINV.WD.GD.ZS",   # FDI, net inflows (% of GDP)
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "nigeria_monetary_data.csv")


def fetch_indicator(country: str, indicator: str, per_page: int = 300) -> pd.DataFrame:
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {"format": "json", "per_page": per_page}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if len(payload) < 2 or payload[1] is None:
        raise ValueError(f"No data returned for indicator {indicator}.")

    df = pd.DataFrame(payload[1])[["date", "value"]]
    df = df.rename(columns={"date": "year", "value": indicator})
    df["year"] = df["year"].astype(int)
    return df


def main():
    merged = None
    for var_name, code in INDICATORS.items():
        print(f"Fetching {var_name} ({code})...")
        df = fetch_indicator(COUNTRY_CODE, code).rename(columns={code: var_name})
        merged = df if merged is None else merged.merge(df, on="year", how="outer")

    merged = merged[(merged["year"] >= START_YEAR) & (merged["year"] <= END_YEAR)]
    merged = merged.sort_values("year").reset_index(drop=True)

    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(merged)} rows to {OUTPUT_PATH}")
    print(merged.head())
    print("...")
    print(merged.tail())

    missing = merged.isna().sum()
    if missing.any():
        print("\nNote: some years have missing values (World Bank hasn't published yet, "
              "or the series doesn't cover that year):")
        print(missing[missing > 0])


if __name__ == "__main__":
    main()
