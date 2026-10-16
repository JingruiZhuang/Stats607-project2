"""Data-generating mechanisms for scenarios A and B."""

import numpy as np
import pandas as pd

from . import config

COVARIATES = ["V1", "V2", "V3", "V4"]


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def add_indicators(data):
    """Append ``Il`` = ``1(Vl > 0)`` for every covariate present."""
    out = data.copy()
    for v in COVARIATES:
        if v in out.columns:
            out["I" + v[1:]] = (out[v] > 0).astype(float)
    return out


def design_matrix(data, terms):
    """Build a design matrix from a list of term strings.

    Terms are evaluated against the columns of ``data``; ``"1"`` becomes an
    intercept column.  Keeping specifications as strings means the correct and
    false models differ only by a list in ``config``, with no duplicated code.
    """
    n = len(data)
    namespace = {c: data[c].to_numpy(dtype=float) for c in data.columns}
    columns = []
    for term in terms:
        if term.strip() == "1":
            columns.append(np.ones(n))
        else:
            value = eval(term, {"__builtins__": {}}, namespace)
            columns.append(np.asarray(value, dtype=float))
    return np.column_stack(columns)


def linear_predictor(data, spec):
    """Evaluate a specification with known coefficients."""
    coefficients = spec.get("beta", spec.get("alpha"))
    return design_matrix(data, spec["terms"]) @ np.asarray(coefficients, dtype=float)


def with_treatment(data, value):
    """Copy of ``data`` with the treatment indicator fixed at ``value``.

    Used to read off potential outcomes when verifying the true estimand.
    """
    out = data.copy()
    out["D"] = float(value)
    return out


def generate(scenario, n, rng):
    """Draw one dataset of size ``n`` for scenario ``"A"`` or ``"B"``.

    Returns ``V1..V4``, ``I1..I4``, ``D``, ``Y_full`` and ``Y``.  ``V4`` is a
    noise covariate used only by the false propensity model in scenario B.
    ``Y_full`` is the complete-data outcome, retained for DGP checks; the
    estimators see only ``Y``, which is missing where ``D == 0`` in scenario A.
    """
    spec = config.SCENARIOS[scenario]

    data = pd.DataFrame({v: rng.standard_normal(n) for v in COVARIATES})
    data = add_indicators(data)

    propensity = expit(linear_predictor(data, spec["ps_true"]))
    data["D"] = rng.binomial(1, propensity).astype(float)

    data["Y_full"] = linear_predictor(data, spec["or_true"]) + rng.standard_normal(n)

    if scenario == "A":
        data["Y"] = np.where(data["D"] == 1.0, data["Y_full"], np.nan)
    else:
        data["Y"] = data["Y_full"]

    return data
