"""Method correctness: the estimators recover the truth in an easy case."""

import pytest

from src import config, dgps, methods


def test_sanity_condition():
    """With pi = 0.5 and a correct linear outcome model, HT, OR and DR agree
    with each other and with the true value."""
    pytest.skip("not implemented")


def test_dr_equals_or_when_both_correct():
    """DR is close to OR when both nuisance models are correct."""
    pytest.skip("not implemented")
