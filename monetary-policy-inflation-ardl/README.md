# 🇳🇬 Monetary Policy & Inflation in Nigeria — ARDL Model Dashboard

An interactive dashboard that turns an academic ARDL econometric study
(monetary policy's effect on inflation in Nigeria, 1985–2022) into a live,
explorable, reproducible data science project.

**[Live demo →](#)** *(add your Streamlit Cloud link here once deployed)*

## Background

Based on an academic thesis modeling:

```
INFL = f(INT, EXC, MS, FDI)
```

where INFL = inflation rate, INT = interest rate, EXC = exchange rate,
MS = money supply, FDI = foreign direct investment inflows.

The original study used CBN Statistical Bulletin / NBS data in Eviews 10,
applying: ADF unit root tests → ARDL bounds cointegration test → short-run
and long-run coefficients → error correction model → diagnostic tests.

## What this project adds

Rather than just displaying the thesis's static results, this project
**re-runs the same methodology live** on World Bank data using Python
(`statsmodels`), and shows the two side by side:

- **"As reported in the thesis"** — the original numbers, exactly as
  written up
- **"Live replication"** — this project's own fresh computation

The two will not match exactly — different data source, different exact
variable definitions (e.g. lending rate vs. monetary policy rate), different
vintage. **That's shown deliberately, not hidden.** The value of this
project is demonstrating that you can (a) understand and reproduce a real
econometric methodology in code, and (b) be honest about what does and
doesn't replicate — which is a more credible skill to show a client or
employer than a dashboard that quietly pretends everything lines up.

## Structure

```
monetary-policy-inflation-ardl/
├── data/
│   ├── fetch_data.py              # pulls INFL, INT, EXC, MS, FDI from World Bank API
│   └── nigeria_monetary_data.csv  # generated after running fetch_data.py
├── analysis.py                    # ADF tests, ARDL/UECM bounds test, long-run coefficients
├── thesis_results.py              # original thesis figures, hardcoded and clearly labeled
├── app.py                         # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Running it

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt

python data/fetch_data.py   # pulls the 5 variables from World Bank
python analysis.py          # sanity-check the econometrics in the terminal first
streamlit run app.py        # launch the dashboard
```

## Methodology notes

- **Unit root testing**: Augmented Dickey-Fuller, constant + trend, matching
  the thesis's specification
- **Cointegration**: ARDL bounds test (Pesaran, Shin & Smith 2001) via
  `statsmodels.tsa.ardl.UECM`, case 5 (unrestricted intercept and trend),
  matching the thesis's inclusion of `@TREND`
- **Long-run coefficients**: derived from the unrestricted error correction
  model as `-coefficient(x.L1) / coefficient(y.L1)`
- Fixed lag structure (lags=1, order=1) is used for the live model as a
  reasonable default — a natural extension is to run `ardl_select_order`
  for AIC-optimal lag selection and compare that to the thesis's ARDL(2,3,2,1,0)

## Known limitations (stated on purpose)

- World Bank annual series won't perfectly match CBN/NBS-sourced data
- Fixed lag order in the live model vs. the thesis's more complex
  ARDL(2,3,2,1,0) specification
- No exogenous structural break handling (e.g. 2023 subsidy removal, COVID)

## Author

Built by [Your Name] — economist working at the intersection of economic
theory and applied data science.
