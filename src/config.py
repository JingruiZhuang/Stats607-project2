"""Simulation parameters for the Bang & Robins (2005) reproduction.

All design choices live here; the other modules read from this file and hold no
hardcoded constants.  Model specifications are lists of term strings that
``dgps.design_matrix`` evaluates against a data frame, where ``V1..V4`` are the
covariates, ``D`` is the missingness/treatment indicator and ``I1..I4`` are the
indicators ``1(Vl > 0)``.
"""

MASTER_SEED = 20251016
N = 500
N_SIM = 1000

RAW_PATH = "results/raw/estimates.csv"
SUMMARY_PATH = "results/raw/summary.csv"
FIGURE_DIR = "results/figures"

SCENARIOS = {
    "A": {
        "label": "Missing data, mu = E(Y)",
        "truth": 1.0,
        "or_true": {
            "terms": ["1", "V1**2", "V2", "V2*V3"],
            "beta": [0.0, 1.0, 2.5, 3.0],
        },
        "ps_true": {
            "terms": ["1", "I1", "I2", "I3", "I1*I2"],
            "alpha": [-1.0, 1.0, 0.0, 0.0, -1.0],
        },
        "or_false": {"terms": ["1", "V1", "V2**2"]},
        "ps_false": {"terms": ["1", "I1", "I3"]},
    },
    "B": {
        "label": "Treatment effect, ATE",
        "truth": 2.0,
        "or_true": {
            "terms": ["1", "V1**2*D", "V2*D", "V2*V3*(1-D)", "V3*(1-D)"],
            "beta": [0.0, 2.0, 3.0, 2.0, -4.0],
        },
        "ps_true": {
            "terms": ["1", "I1", "I2", "I3", "I1*I2"],
            "alpha": [-3.0, 2.5, 3.0, 1.0, -3.0],
        },
        "or_false": {"terms": ["1", "V1*D", "V2**2*(1-D)"]},
        "ps_false": {"terms": ["1", "I3", "V4"]},
    },
}

# (name, estimator family, propensity model, outcome regression model)
ESTIMATORS = [
    ("HT",        "ht", "ps_true",  None),
    ("HT.fal",    "ht", "ps_false", None),
    ("OR",        "or", None,       "or_true"),
    ("OR.fal",    "or", None,       "or_false"),
    ("DR",        "dr", "ps_true",  "or_true"),
    ("DR.ofal",   "dr", "ps_true",  "or_false"),
    ("DR.pfal",   "dr", "ps_false", "or_true"),
    ("DR.o+pfal", "dr", "ps_false", "or_false"),
]

# Beyond the reproduction: the phi1 = phi2 variant proposed in Section 2.2 of the
# paper, which turns out not to be doubly robust for the treatment effect.
EXTENSION_ESTIMATORS = [
    ("DR1",        "dr1", "ps_true",  "or_true"),
    ("DR1.ofal",   "dr1", "ps_true",  "or_false"),
    ("DR1.pfal",   "dr1", "ps_false", "or_true"),
    ("DR1.o+pfal", "dr1", "ps_false", "or_false"),
]

# Published Table 2 values, for output validation and the comparison table.
PUBLISHED = {
    ("A", "HT"):        {"bias_mean": -0.01, "variance": 0.11, "bias_median":  0.00, "iqr": 0.43},
    ("A", "HT.fal"):    {"bias_mean": -0.31, "variance": 0.12, "bias_median": -0.29, "iqr": 0.44},
    ("A", "OR"):        {"bias_mean":  0.00, "variance": 0.04, "bias_median":  0.00, "iqr": 0.28},
    ("A", "OR.fal"):    {"bias_mean": -0.36, "variance": 0.12, "bias_median": -0.35, "iqr": 0.44},
    ("A", "DR"):        {"bias_mean":  0.00, "variance": 0.04, "bias_median":  0.00, "iqr": 0.28},
    ("A", "DR.ofal"):   {"bias_mean": -0.02, "variance": 0.11, "bias_median":  0.00, "iqr": 0.45},
    ("A", "DR.pfal"):   {"bias_mean":  0.00, "variance": 0.04, "bias_median":  0.00, "iqr": 0.28},
    ("A", "DR.o+pfal"): {"bias_mean": -0.32, "variance": 0.12, "bias_median": -0.30, "iqr": 0.45},
    ("B", "HT"):        {"bias_mean": -0.01, "variance": 0.21, "bias_median":  0.00, "iqr": 0.59},
    ("B", "HT.fal"):    {"bias_mean":  0.86, "variance": 0.15, "bias_median":  0.87, "iqr": 0.52},
    ("B", "OR"):        {"bias_mean":  0.00, "variance": 0.07, "bias_median":  0.01, "iqr": 0.35},
    ("B", "OR.fal"):    {"bias_mean": -1.56, "variance": 0.07, "bias_median": -1.56, "iqr": 0.34},
    ("B", "DR"):        {"bias_mean":  0.00, "variance": 0.09, "bias_median":  0.01, "iqr": 0.41},
    ("B", "DR.ofal"):   {"bias_mean": -0.09, "variance": 0.28, "bias_median": -0.06, "iqr": 0.63},
    ("B", "DR.pfal"):   {"bias_mean":  0.00, "variance": 0.08, "bias_median":  0.01, "iqr": 0.39},
    ("B", "DR.o+pfal"): {"bias_mean":  0.92, "variance": 0.15, "bias_median":  0.93, "iqr": 0.54},
}
