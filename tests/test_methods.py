"""Method correctness: the estimators recover known values in easy cases."""

import numpy as np
import pandas as pd

from src import config, dgps, methods

INTERCEPT_ONLY = {"terms": ["1"]}


def _randomised_data(scenario, n, rng):
    """A sanity-check dataset: treatment or missingness completely at random
    with probability 0.5, and an outcome linear in the covariates, so every
    estimator should recover the truth.
    """
    data = dgps.add_indicators(
        pd.DataFrame({v: rng.standard_normal(n) for v in dgps.COVARIATES})
    )
    data["D"] = rng.binomial(1, 0.5, n).astype(float)
    mean = 1.0 + 2.0 * data["V1"]
    if scenario == "B":
        mean = mean + 3.0 * data["D"]
    data["Y_full"] = mean + rng.standard_normal(n)
    data["Y"] = np.where(data["D"] == 1.0, data["Y_full"], np.nan) \
        if scenario == "A" else data["Y_full"]
    return data


def test_sanity_condition():
    """With pi = 0.5 and a correct linear outcome model, all three estimators
    agree with each other and with the true value."""
    for scenario, truth, terms in (("A", 1.0, ["1", "V1"]),
                                   ("B", 3.0, ["1", "V1", "D"])):
        data = _randomised_data(scenario, 50_000, np.random.default_rng(21))
        or_spec = {"terms": terms}
        estimates = [
            methods.estimate_ht(data, scenario, INTERCEPT_ONLY),
            methods.estimate_or(data, scenario, or_spec),
            methods.estimate_dr(data, scenario, INTERCEPT_ONLY, or_spec),
        ]
        for value in estimates:
            assert abs(value - truth) < 0.1, (scenario, estimates)
        assert max(estimates) - min(estimates) < 0.1, (scenario, estimates)


def test_doubly_robust_under_one_correct_model():
    """DR recovers the estimand whenever either nuisance model is correct."""
    for scenario in ("A", "B"):
        spec = config.SCENARIOS[scenario]
        data = dgps.generate(scenario, 100_000, np.random.default_rng(22))
        for ps, orm in (("ps_true", "or_true"),
                        ("ps_true", "or_false"),
                        ("ps_false", "or_true")):
            value = methods.estimate_dr(data, scenario, spec[ps], spec[orm])
            assert abs(value - spec["truth"]) < 0.1, (scenario, ps, orm, value)


def test_constrained_variant_is_not_doubly_robust():
    """The phi1 = phi2 variant of Section 2.2 loses double robustness for the
    treatment effect: with a correct propensity model but a false outcome
    model it does not converge to the true effect."""
    spec = config.SCENARIOS["B"]
    data = dgps.generate("B", 100_000, np.random.default_rng(23))
    unconstrained = methods.estimate_dr(data, "B", spec["ps_true"], spec["or_false"])
    constrained = methods.estimate_dr(data, "B", spec["ps_true"], spec["or_false"],
                                      constrained=True)
    assert abs(unconstrained - spec["truth"]) < 0.1
    assert abs(constrained - spec["truth"]) > 1.0
