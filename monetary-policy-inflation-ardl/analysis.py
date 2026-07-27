"""
analysis.py
Replicates the core econometric steps of the thesis (unit root testing,
ARDL bounds cointegration test, long-run coefficients, error-correction
speed of adjustment) using the World-Bank-sourced dataset.

Numbers here will NOT exactly match the thesis's original Eviews output —
that used CBN Statistical Bulletin data. What matters for this project is
that the *methodology* is real and runs end-to-end on real data, and that
the dashboard is honest about which numbers are "as reported in the thesis"
vs. "this project's own replication."

Run with:
    python analysis.py
"""

import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.ardl import UECM

DATA_PATH = "data/nigeria_monetary_data.csv"
VARIABLES = ["INFL", "INT", "EXC", "MS", "FDI"]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH).set_index("year")
    df = df.dropna()  # ARDL/UECM needs a complete, unbroken series
    return df


def adf_test(series: pd.Series, name: str) -> dict:
    """Run ADF with constant + trend, at level and first difference."""
    level_stat, level_p, *_ = adfuller(series, regression="ct", autolag="AIC")
    diff_stat, diff_p, *_ = adfuller(series.diff().dropna(), regression="ct", autolag="AIC")

    order = "I(0)" if level_p < 0.05 else "I(1)"
    return {
        "variable": name,
        "level_stat": level_stat,
        "level_p": level_p,
        "diff_stat": diff_stat,
        "diff_p": diff_p,
        "order_of_integration": order,
    }


def run_unit_root_tests(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Unit Root Tests (ADF, constant + trend) ===")
    results = [adf_test(df[var], var) for var in VARIABLES]
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    return results_df


def run_ardl_bounds_test(df: pd.DataFrame, lags: int = 1, order: int = 1):
    print("\n=== ARDL Bounds Cointegration Test (Pesaran, Shin & Smith) ===")
    endog = df["INFL"]
    exog = df[["INT", "EXC", "MS", "FDI"]]

    uecm = UECM(endog, lags=lags, exog=exog, order=order, trend="ct")
    res = uecm.fit()

    bounds = res.bounds_test(case=5)  # unrestricted intercept & trend, matching thesis's @TREND
    print(bounds)

    # Long-run coefficients derived from the unrestricted ECM:
    # long-run coefficient of x = -(coefficient on x.L1) / (coefficient on INFL.L1)
    params = res.params
    ecm_speed = params["INFL.L1"]
    long_run = {}
    for var in ["INT", "EXC", "MS", "FDI"]:
        col = f"{var}.L1"
        if col in params:
            long_run[var] = -params[col] / ecm_speed

    print(f"\nError-correction speed of adjustment (INFL.L1 coefficient): {ecm_speed:.4f}")
    print("Long-run coefficients (implied by the unrestricted ECM):")
    for var, coef in long_run.items():
        print(f"  {var}: {coef:.6f}")

    return res, bounds, long_run, ecm_speed


def main():
    df = load_data()
    print(f"Loaded {len(df)} complete yearly observations: {df.index.min()}-{df.index.max()}")

    run_unit_root_tests(df)
    run_ardl_bounds_test(df)


if __name__ == "__main__":
    main()
