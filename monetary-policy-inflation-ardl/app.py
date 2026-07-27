"""
app.py
Monetary Policy & Inflation in Nigeria — an ARDL model dashboard.

Two things are shown side by side, always clearly labeled:
  1. "As reported in the thesis" — the original results (CBN/NBS data, Eviews 10)
  2. "Live replication" — this project's own run of the same methodology on
     World Bank data, computed fresh each time the data is refreshed

Run with:
    streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import thesis_results as thesis
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.ardl import UECM

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "nigeria_monetary_data.csv")

st.set_page_config(page_title="Monetary Policy & Inflation (Nigeria)", layout="wide")

st.title("🇳🇬 Monetary Policy & Inflation in Nigeria — ARDL Model")
st.caption(
    "Based on an academic ARDL study (1985–2022). Model: "
    "INFL = f(INT, EXC, MS, FDI). Original results are from CBN/NBS-sourced "
    "data via Eviews 10; the live panels below re-run the same methodology "
    "on World Bank data as a transparent, reproducible companion — the two "
    "will not match exactly, and that's shown deliberately rather than hidden."
)

st.latex(r"INFL_t = \beta_0 + \beta_1 INT_t + \beta_2 EXC_t + \beta_3 MS_t + \beta_4 FDI_t + \varepsilon_t")


@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    return pd.read_csv(DATA_PATH).dropna()


df = load_data()

if df is None or df.empty:
    st.error("No data found. Run `python data/fetch_data.py` first, then refresh this page.")
    st.stop()

# ---------------------------------------------------------------
# 1. Historical series
# ---------------------------------------------------------------
st.header("1. Historical Series")
variable = st.selectbox("Choose a variable to plot", ["INFL", "INT", "EXC", "MS", "FDI"])
fig = px.line(df, x="year", y=variable, markers=True, title=f"{variable} over time (World Bank)")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------
# 2. Descriptive statistics — thesis vs live
# ---------------------------------------------------------------
st.header("2. Descriptive Statistics")
col1, col2 = st.columns(2)

with col1:
    st.subheader("As reported in the thesis")
    thesis_stats_df = pd.DataFrame(thesis.DESCRIPTIVE_STATS).T
    st.dataframe(thesis_stats_df, use_container_width=True)

with col2:
    st.subheader("Live (World Bank data)")
    live_stats_df = df[["INFL", "INT", "EXC", "MS", "FDI"]].describe().T[["mean", "50%", "max", "min", "std"]]
    live_stats_df.columns = ["mean", "median", "max", "min", "std"]
    st.dataframe(live_stats_df, use_container_width=True)

# ---------------------------------------------------------------
# 3. Unit root tests — thesis vs live
# ---------------------------------------------------------------
st.header("3. Unit Root Tests (ADF, constant + trend)")


@st.cache_data
def run_live_adf(data: pd.DataFrame):
    rows = []
    for var in ["INFL", "INT", "EXC", "MS", "FDI"]:
        level_stat, level_p, *_ = adfuller(data[var], regression="ct", autolag="AIC")
        diff_stat, diff_p, *_ = adfuller(data[var].diff().dropna(), regression="ct", autolag="AIC")
        order = "I(0)" if level_p < 0.05 else "I(1)"
        rows.append({
            "Variable": var, "Level t-stat": round(level_stat, 4), "Level p": round(level_p, 4),
            "Diff t-stat": round(diff_stat, 4), "Diff p": round(diff_p, 4), "Order": order,
        })
    return pd.DataFrame(rows)


col1, col2 = st.columns(2)
with col1:
    st.subheader("As reported in the thesis")
    thesis_ur = pd.DataFrame(thesis.UNIT_ROOT_RESULTS).T
    thesis_ur.columns = ["Level t-stat", "Level p", "Diff t-stat", "Diff p", "Order"]
    st.dataframe(thesis_ur, use_container_width=True)

with col2:
    st.subheader("Live (World Bank data)")
    live_ur = run_live_adf(df)
    st.dataframe(live_ur.set_index("Variable"), use_container_width=True)

# ---------------------------------------------------------------
# 4. ARDL bounds test + long-run coefficients (live only — see note)
# ---------------------------------------------------------------
st.header("4. ARDL Bounds Test & Long-Run Coefficients")
st.caption(
    "The bounds test and long-run coefficients below are computed live on "
    "the World Bank dataset using statsmodels' UECM (unrestricted error "
    "correction model), matching the thesis's Pesaran-Shin-Smith methodology."
)


@st.cache_data
def run_live_ardl(data: pd.DataFrame):
    endog = data["INFL"]
    exog = data[["INT", "EXC", "MS", "FDI"]]
    uecm = UECM(endog, lags=1, exog=exog, order=1, trend="ct")
    res = uecm.fit()
    bounds = res.bounds_test(case=5)

    params = res.params
    ecm_speed = params["INFL.L1"]
    long_run = {
        var: -params[f"{var}.L1"] / ecm_speed
        for var in ["INT", "EXC", "MS", "FDI"] if f"{var}.L1" in params
    }
    return bounds, long_run, ecm_speed


try:
    bounds, long_run, ecm_speed = run_live_ardl(df)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Bounds test — as reported in thesis")
        st.metric("F-statistic", f"{thesis.BOUNDS_TEST['f_statistic']:.2f}")
        st.write(thesis.BOUNDS_TEST["critical_values"])
        st.success(thesis.BOUNDS_TEST["conclusion"])

    with col2:
        st.subheader("Bounds test — live replication")
        st.metric("F-statistic", f"{bounds.stat:.2f}")
        upper_p = bounds.p_values["upper"]
        st.write(f"Upper p-value: {upper_p:.4g}")
        conclusion = "Evidence of cointegration" if upper_p < 0.05 else "Inconclusive / no strong evidence"
        st.success(conclusion) if upper_p < 0.05 else st.warning(conclusion)

    st.subheader("Long-run coefficients: thesis vs. live")
    compare_rows = []
    for var in ["INT", "EXC", "MS", "FDI"]:
        thesis_coef = thesis.LONG_RUN_COEFFICIENTS[var][0]
        live_coef = long_run.get(var, float("nan"))
        compare_rows.append({"Variable": var, "Thesis coefficient": thesis_coef, "Live coefficient": live_coef})
    compare_df = pd.DataFrame(compare_rows)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Thesis (CBN/NBS data)", x=compare_df["Variable"], y=compare_df["Thesis coefficient"]))
    fig.add_trace(go.Bar(name="Live (World Bank data)", x=compare_df["Variable"], y=compare_df["Live coefficient"]))
    fig.update_layout(barmode="group", title="Long-run coefficients: thesis vs. live replication")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Coefficients differ because the two datasets differ in source and "
        "exact definition (e.g. lending rate vs. monetary policy rate). "
        "The point of this panel is methodological transparency, not an "
        "exact match."
    )

    st.metric("Live error-correction speed of adjustment", f"{ecm_speed:.3f}",
              help="Thesis reported CointEq(-1) = -1.234")

except Exception as e:
    st.warning(f"Live ARDL model couldn't be fit on the current dataset ({e}). "
               "This can happen if a year has missing data after merging — "
               "try re-running data/fetch_data.py.")

# ---------------------------------------------------------------
# 5. 3D model visualization
# ---------------------------------------------------------------
st.header("5. 3D Model Visualization")
st.caption(
    "A 3D chart only has 3 spatial axes, so at most 2 regressors can share "
    "one plot with INFL — there's no way to fit all 4 (INT, EXC, MS, FDI) "
    "onto a single 3D surface. Pick a pair below; the surface uses the "
    "live long-run coefficients, holding the other two variables at their "
    "sample mean."
)

REGRESSORS = ["INT", "EXC", "MS", "FDI"]
col_a, col_b = st.columns(2)
with col_a:
    var_x = st.selectbox("X-axis variable", REGRESSORS, index=0)
with col_b:
    var_y = st.selectbox("Y-axis variable", [v for v in REGRESSORS if v != var_x], index=0)

try:
    _, long_run_3d, ecm_speed_3d = run_live_ardl(df)  # reuse already-fitted model
    const_approx = df["INFL"].mean() - sum(long_run_3d[v] * df[v].mean() for v in REGRESSORS)

    x_range = np.linspace(df[var_x].min(), df[var_x].max(), 30)
    y_range = np.linspace(df[var_y].min(), df[var_y].max(), 30)
    x_grid, y_grid = np.meshgrid(x_range, y_range)

    other_vars = [v for v in REGRESSORS if v not in (var_x, var_y)]
    other_contribution = sum(long_run_3d[v] * df[v].mean() for v in other_vars)

    z_grid = (
        const_approx
        + long_run_3d[var_x] * x_grid
        + long_run_3d[var_y] * y_grid
        + other_contribution
    )

    fig3d = go.Figure()
    fig3d.add_trace(go.Surface(x=x_range, y=y_range, z=z_grid, opacity=0.6, showscale=False, name="Model surface"))
    fig3d.add_trace(go.Scatter3d(
        x=df[var_x], y=df[var_y], z=df["INFL"],
        mode="markers", marker=dict(size=4, color=df["year"], colorscale="Viridis", showscale=True),
        name="Actual data (colored by year)",
    ))
    fig3d.update_layout(
        title=f"INFL vs. {var_x} and {var_y} — live long-run model surface",
        scene=dict(xaxis_title=var_x, yaxis_title=var_y, zaxis_title="INFL"),
        height=650,
    )
    st.plotly_chart(fig3d, use_container_width=True)
    st.caption(f"{', '.join(other_vars)} held at sample mean for this view.")

except Exception as e:
    st.warning(f"Couldn't build the 3D surface ({e}). Make sure the live ARDL model above fit successfully.")

st.subheader("All variables together — parallel coordinates")
st.caption(
    "Each vertical axis is one variable; each line is one year, crossing "
    "all five axes. This is the practical way to see every variable at "
    "once without picking pairs."
)
parcoords_df = df[["year", "INFL", "INT", "EXC", "MS", "FDI"]].copy()
fig_parcoords = go.Figure(data=go.Parcoords(
    line=dict(color=parcoords_df["year"], colorscale="Viridis", showscale=True),
    dimensions=[
        dict(label=col, values=parcoords_df[col]) for col in ["INFL", "INT", "EXC", "MS", "FDI"]
    ],
))
fig_parcoords.update_layout(height=450)
st.plotly_chart(fig_parcoords, use_container_width=True)

# ---------------------------------------------------------------
# 6. Diagnostics (thesis)
# ---------------------------------------------------------------
st.header("6. Diagnostic Tests (as reported in the thesis)")
diag_cols = st.columns(3)
for col, (key, d) in zip(diag_cols, thesis.DIAGNOSTICS.items()):
    with col:
        st.metric(d["test"], f"p = {d['p_value']:.3f}")
        st.caption(d["conclusion"])

st.divider()
st.caption(
    "Built as a reproducibility-focused companion to an academic ARDL thesis "
    "on monetary policy and inflation in Nigeria. Data: World Bank Open Data. "
    "Thesis figures: CBN Statistical Bulletin / NBS via Eviews 10."
)