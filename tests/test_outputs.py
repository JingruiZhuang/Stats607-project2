"""Output validation and reproducibility."""

import numpy as np
import pytest

from src import config, metrics


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


def test_matches_published_values():
    """Each cell's bias is within Monte Carlo error of the published Table 2
    value."""
    pytest.skip("not implemented")


def test_same_seed_same_results(tmp_path):
    """Rerunning with the same seed gives identical estimates, a scenario run
    on its own draws the same data as in a full run, and a short run reproduces
    the leading replicates of a longer one."""
    from src import simulation

    def go(n_sim, scenarios):
        return simulation.run(scenarios, config.N, n_sim, config.MASTER_SEED,
                              str(tmp_path / f"{n_sim}-{''.join(scenarios)}.csv"))

    both = go(4, ["A", "B"])
    assert both.equals(go(4, ["A", "B"]))

    only_b = go(4, ["B"])
    assert both[both.scenario == "B"].reset_index(drop=True).equals(only_b)

    shorter = go(2, ["A", "B"])
    assert both[both.replicate < 2].reset_index(drop=True).equals(shorter)
