"""DGP verification: the generated data has the properties the design claims."""

import numpy as np
import pytest

from src import config, dgps


def test_scenario_a_marginal_mean():
    """E(Y) = 1 in scenario A at a large sample size."""
    pytest.skip("not implemented")


def test_scenario_b_ate():
    """E{Y(1)} - E{Y(0)} = 2 in scenario B at a large sample size."""
    pytest.skip("not implemented")


def test_indicators_and_design_matrix():
    """I1..I4 are 1(Vl > 0) and term strings map to the right columns."""
    pytest.skip("not implemented")
