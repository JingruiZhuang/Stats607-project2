"""Performance measures, with Monte Carlo standard errors."""

import numpy as np
import pandas as pd

N_BOOTSTRAP = 2000


def performance(estimates, truth, rng=None):
    """Summarise one cell's estimates.

    Returns the four measures of Table 2 together with their Monte Carlo
    standard errors, which say how much of any gap from the published values is
    simulation noise.  The standard errors of the mean and of the variance have
    closed forms; those of the median and the interquartile range do not, so
    they are bootstrapped over replicates.
    """
    values = np.asarray(estimates, dtype=float)
    n = values.size
    variance = values.var(ddof=1)
    quartiles = np.percentile(values, [25, 75])

    if rng is None:
        rng = np.random.default_rng(0)
    resamples = values[rng.integers(0, n, size=(N_BOOTSTRAP, n))]
    median_se = np.median(resamples, axis=1).std(ddof=1)
    iqr_se = np.diff(np.percentile(resamples, [25, 75], axis=1), axis=0).std(ddof=1)

    return {
        "n_replicates": n,
        "bias_mean": values.mean() - truth,
        "bias_mean_se": np.sqrt(variance / n),
        "bias_median": np.median(values) - truth,
        "bias_median_se": median_se,
        "variance": variance,
        "variance_se": variance * np.sqrt(2.0 / (n - 1)),
        "iqr": quartiles[1] - quartiles[0],
        "iqr_se": float(iqr_se),
    }


def summarise(raw, truths, published=None, seed=0):
    """Collapse the long-format estimates frame into one row per cell.

    Where published values are supplied, the gap from the reproduction is
    reported in units of its own Monte Carlo standard error, so that cells
    needing explanation can be told from cells that merely wobbled.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for (scenario, estimator), group in raw.groupby(["scenario", "estimator"], sort=False):
        row = {"scenario": scenario, "estimator": estimator}
        row.update(performance(group["estimate"], truths[scenario], rng))

        if published is not None:
            target = published.get((scenario, estimator))
            for measure in ("bias_mean", "bias_median", "variance", "iqr"):
                reference = target.get(measure) if target else None
                row["published_" + measure] = reference
                row["z_" + measure] = (
                    (row[measure] - reference) / row[measure + "_se"]
                    if reference is not None and row[measure + "_se"] > 0
                    else None
                )
        rows.append(row)

    return pd.DataFrame(rows)
