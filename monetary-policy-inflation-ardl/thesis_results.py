"""
thesis_results.py
The original results as reported in the academic thesis (Eviews 10, CBN/NBS
data, 1985-2022). Kept as a separate, clearly-labeled module so the
dashboard can show "as reported in the thesis" alongside "this project's
own live replication with World Bank data" without ever mixing the two.
"""

DESCRIPTIVE_STATS = {
    "INFL": {"mean": 19.25319, "median": 12.87658, "max": 72.83550, "min": 5.388008, "std": 16.99914},
    "INT": {"mean": 11.20779, "median": 10.28833, "max": 23.24167, "min": 4.206848, "std": 4.105270},
    "EXC": {"mean": 511.9713, "median": 522.4256, "max": 984.5611, "min": 264.6918, "std": 145.9457},
    "MS": {"mean": 1.55e13, "median": 2.74e12, "max": 7.87e13, "min": 95.98768, "std": 2.20e13},
    "FDI": {"mean": 2.570793, "median": 2.255634, "max": 8.070257, "min": 0.135178, "std": 2.061316},
}

UNIT_ROOT_RESULTS = {
    # variable: (level t-stat, level p, first-diff t-stat, first-diff p, order)
    "INFL": (-2.3022, 0.4205, -4.5667, 0.0055, "I(1)"),
    "INT": (-5.1758, 0.0009, -4.1770, 0.0120, "I(0)"),
    "EXC": (-1.4033, 0.8439, -3.7615, 0.0303, "I(1)"),
    "MS": (-2.6532, 0.2606, -3.8281, 0.0267, "I(1)"),
    "FDI": (-2.6712, 0.2535, -6.4446, 0.0000, "I(1)"),
}

BOUNDS_TEST = {
    "f_statistic": 11.39058,
    "k": 4,
    "critical_values": {
        "10%": {"I0": 3.334, "I1": 4.438},
        "5%": {"I0": 3.958, "I1": 5.226},
        "1%": {"I0": 5.376, "I1": 7.092},
    },
    "conclusion": "Reject null of no long-run relationship at all significance levels.",
}

LONG_RUN_COEFFICIENTS = {
    # variable: (coefficient, std error, t-stat, p-value)
    "INT": (1.507641, 0.762571, 1.977050, 0.0607),
    "EXC": (-0.028555, 0.017069, -1.672868, 0.1085),
    "MS": (4.37e-13, 1.89e-13, 2.318826, 0.0301),
    "FDI": (-0.756160, 1.066352, -0.709109, 0.4857),
}

ECM_SPEED_OF_ADJUSTMENT = -1.233711  # CointEq(-1) coefficient
ECM_P_VALUE = 0.0000

DIAGNOSTICS = {
    "serial_correlation": {"test": "Breusch-Godfrey LM", "f_stat": 1.217391, "p_value": 0.3170, "conclusion": "No serial correlation"},
    "heteroskedasticity": {"test": "Breusch-Pagan-Godfrey", "f_stat": 1.331947, "p_value": 0.2677, "conclusion": "No heteroskedasticity"},
    "normality": {"test": "Jarque-Bera (residuals)", "p_value": 0.615098, "conclusion": "Residuals normally distributed"},
}
