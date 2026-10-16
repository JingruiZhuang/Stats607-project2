"""Output validation and reproducibility."""

import pytest

from src import config, metrics


def test_performance_measures_in_range():
    """Variances are positive, IQRs are positive, biases are finite."""
    pytest.skip("not implemented")


def test_matches_published_values():
    """Each cell's bias is within Monte Carlo error of the published Table 2
    value."""
    pytest.skip("not implemented")


def test_same_seed_same_results():
    """Rerunning a replicate with the same seed gives identical estimates."""
    pytest.skip("not implemented")
