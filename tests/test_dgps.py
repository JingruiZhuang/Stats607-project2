"""DGP verification: the generated data has the properties the design claims."""

import numpy as np
import pandas as pd

from src import config, dgps

N_LARGE = 200_000


def test_scenario_a_marginal_mean():
    """E(Y) = 1 in scenario A, as the coefficients in Table 1A imply."""
    data = dgps.generate("A", N_LARGE, np.random.default_rng(11))
    assert abs(data["Y_full"].mean() - config.SCENARIOS["A"]["truth"]) < 0.02


def test_scenario_b_ate():
    """E{Y(1)} - E{Y(0)} = 2 in scenario B, as Table 1B implies."""
    data = dgps.generate("B", N_LARGE, np.random.default_rng(12))
    spec = config.SCENARIOS["B"]["or_true"]
    treated = dgps.linear_predictor(dgps.with_treatment(data, 1), spec).mean()
    control = dgps.linear_predictor(dgps.with_treatment(data, 0), spec).mean()
    assert abs((treated - control) - config.SCENARIOS["B"]["truth"]) < 0.05


def test_missingness_pattern():
    """Y is missing exactly where D = 0 in scenario A, and never in scenario B."""
    a = dgps.generate("A", 2000, np.random.default_rng(13))
    assert a["Y"].isna().equals(a["D"] == 0.0)
    assert a["Y"].notna().any() and a["Y"].isna().any()

    b = dgps.generate("B", 2000, np.random.default_rng(14))
    assert b["Y"].notna().all()


def test_indicators():
    """Il is 1(Vl > 0) for every covariate."""
    data = dgps.add_indicators(pd.DataFrame({"V1": [-1.0, 0.0, 2.0]}))
    assert data["I1"].tolist() == [0.0, 0.0, 1.0]


def test_design_matrix_terms():
    """Term strings map to the columns they name, with "1" as the intercept."""
    data = pd.DataFrame({"V1": [2.0, 3.0], "V2": [1.0, 2.0], "D": [1.0, 0.0]})
    built = dgps.design_matrix(data, ["1", "V1**2", "V2*(1-D)"])
    expected = np.array([[1.0, 4.0, 0.0], [1.0, 9.0, 2.0]])
    assert np.allclose(built, expected)
