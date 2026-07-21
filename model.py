"""
model.py
Simple ARIMA forecasting for Nigeria's inflation rate.

Kept intentionally simple for the MVP — a place to make the model smarter
later (SARIMA for seasonality, Prophet, exogenous variables like exchange
rate or oil price, etc.)
"""

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def forecast_inflation(df: pd.DataFrame, periods: int = 5, order=(2, 1, 2)) -> pd.DataFrame:
    """
    Fit an ARIMA model on historical inflation data and forecast forward.

    Args:
        df: DataFrame with columns ['year', 'inflation_rate'], sorted ascending.
        periods: number of future years to forecast.
        order: ARIMA(p, d, q) order.

    Returns:
        DataFrame with columns ['year', 'inflation_rate', 'type'] where
        type is 'historical' or 'forecast', ready to plot.
    """
    series = df.set_index("year")["inflation_rate"]

    model = ARIMA(series, order=order)
    fitted = model.fit()

    forecast_result = fitted.get_forecast(steps=periods)
    forecast_values = forecast_result.predicted_mean

    last_year = int(series.index[-1])
    future_years = [last_year + i for i in range(1, periods + 1)]

    historical_df = df.copy()
    historical_df["type"] = "historical"

    forecast_df = pd.DataFrame({
        "year": future_years,
        "inflation_rate": forecast_values.values,
        "type": "forecast",
    })

    combined = pd.concat([historical_df, forecast_df], ignore_index=True)
    return combined
