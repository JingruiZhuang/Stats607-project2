"""Performance measures, with Monte Carlo standard errors."""

import numpy as np


def performance(estimates, truth):
    """Return bias in mean, bias in median, variance and IQR, each with its
    Monte Carlo standard error, as a dict."""
    raise NotImplementedError


def summarise(raw, truths):
    """Collapse the long-format estimates frame into one row per cell."""
    raise NotImplementedError
