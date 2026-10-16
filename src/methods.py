"""Estimators: Horvitz-Thompson, outcome regression, and doubly robust."""

import numpy as np


def fit_propensity(data, spec):
    """Fit a logistic model for ``D`` and return fitted probabilities."""
    raise NotImplementedError


def estimate_ht(data, scenario, ps_spec):
    """Horvitz-Thompson estimate of the scenario's estimand."""
    raise NotImplementedError


def estimate_or(data, scenario, or_spec):
    """Outcome-regression estimate: fit by OLS and average fitted values."""
    raise NotImplementedError


def estimate_dr(data, scenario, ps_spec, or_spec):
    """Doubly robust estimate.

    Augments the outcome-regression design with ``1 / pi(V)`` (scenario A) or
    ``1 / f(D | V)`` (scenario B), refits by OLS, then averages the predictions.
    """
    raise NotImplementedError


def estimate(data, scenario, family, ps_spec, or_spec):
    """Dispatch to the estimator named by ``family`` (``ht``, ``or``, ``dr``)."""
    raise NotImplementedError
