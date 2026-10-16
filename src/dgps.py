"""Data-generating mechanisms for scenarios A and B."""

import numpy as np
import pandas as pd


def design_matrix(data, terms):
    """Build a design matrix from a list of term strings.

    Each term is evaluated against the columns of ``data`` (``V1..V4``, ``D``,
    ``I1..I4``); the term ``"1"`` becomes an intercept column.
    """
    raise NotImplementedError


def add_indicators(data):
    """Append ``I1..I4`` = ``1(Vl > 0)`` for every covariate present."""
    raise NotImplementedError


def generate(scenario, n, rng):
    """Draw one dataset of size ``n`` for ``"A"`` or ``"B"``.

    Returns a data frame with ``V1, V2, V3, V4, I1..I4, D, Y``.  In scenario A,
    ``Y`` is NaN where ``D == 0``; in scenario B, ``Y`` is always observed and
    ``D`` is the treatment.
    """
    raise NotImplementedError
