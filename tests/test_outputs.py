"""Output validation and reproducibility."""

import os

import numpy as np
import pandas as pd
import pytest

from src import analyze, config, metrics, simulation

N_SIM_TEST = 300


@pytest.fixture(scope="module")
def summary(tmp_path_factory):
    """A short run of the whole grid, summarised.

    Short enough to keep the suite quick, and seeded from the same master seed,
    so these are the leading replicates of the full run.
    """
    out = tmp_path_factory.mktemp("raw") / "estimates.csv"
    raw = simulation.run(list(config.SCENARIOS), config.N, N_SIM_TEST,
                         config.MASTER_SEED, str(out))
    return analyze.summarise(raw)


def test_performance_measures_recover_known_values():
    """On estimates drawn from a known distribution, the four measures return
    that distribution's bias, variance and interquartile range."""
    rng = np.random.default_rng(31)
    values = rng.normal(1.5, 0.2, 20_000)
    out = metrics.performance(values, truth=1.0, rng=rng)

    assert abs(out["bias_mean"] - 0.5) < 0.01
    assert abs(out["bias_median"] - 0.5) < 0.01
    assert abs(out["variance"] - 0.04) < 0.002
    assert abs(out["iqr"] - 1.349 * 0.2) < 0.01
    assert out["variance"] > 0 and out["iqr"] > 0
    assert all(np.isfinite(v) for v in out.values())


def test_measures_in_valid_ranges(summary):
    """Every cell has a positive variance and interquartile range, finite
    biases, and the expected number of replicates."""
    assert len(summary) == 20
    assert (summary["n_replicates"] == N_SIM_TEST).all()
    assert (summary["variance"] > 0).all()
    assert (summary["iqr"] > 0).all()
    assert np.isfinite(summary[["bias_mean", "bias_median"]].to_numpy()).all()


def test_matches_published_values(summary):
    """Each reproduction cell lands on its Table 2 value.

    The tolerance allows four Monte Carlo standard errors plus 0.005 for the
    rounding of the published values to two decimal places, which for the
    variance and the median is itself comparable to the simulation noise.
    """
    core = summary[summary["published_bias_mean"].notna()]
    assert len(core) == 16

    for measure in ("bias_mean", "bias_median", "variance", "iqr"):
        gap = (core[measure] - core["published_" + measure]).abs()
        tolerance = 4.0 * core[measure + "_se"] + 0.005
        failures = core.loc[gap > tolerance, ["scenario", "estimator"]]
        assert failures.empty, f"{measure} off in {failures.to_dict('records')}"


def test_full_run_summary_is_tighter():
    """Where the committed full run is present, every reproduction cell sits
    within three standard errors of its published bias."""
    if not os.path.exists(config.SUMMARY_PATH):
        pytest.skip(f"{config.SUMMARY_PATH} not present; run `make analyze`")

    full = pd.read_csv(config.SUMMARY_PATH)
    core = full[full["published_bias_mean"].notna()]
    assert len(core) == 16
    assert (core["n_replicates"] == config.N_SIM).all()
    assert core["z_bias_mean"].abs().max() < 3.0


def test_same_seed_same_results(tmp_path):
    """Rerunning with the same seed gives identical estimates, a scenario run
    on its own draws the same data as in a full run, and a short run reproduces
    the leading replicates of a longer one."""
    def go(n_sim, scenarios):
        return simulation.run(scenarios, config.N, n_sim, config.MASTER_SEED,
                              str(tmp_path / f"{n_sim}-{''.join(scenarios)}.csv"))

    both = go(4, ["A", "B"])
    assert both.equals(go(4, ["A", "B"]))

    only_b = go(4, ["B"])
    assert both[both.scenario == "B"].reset_index(drop=True).equals(only_b)

    shorter = go(2, ["A", "B"])
    assert both[both.replicate < 2].reset_index(drop=True).equals(shorter)
