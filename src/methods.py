"""Estimators: Horvitz-Thompson, outcome regression, and doubly robust."""

import numpy as np
import statsmodels.api as sm

from . import config, dgps


def _ols(X, y):
    coefficients, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coefficients


def fit_propensity(data, spec):
    """Fit a logistic model for ``D`` and return the fitted probabilities.

    The specification supplies its own intercept where it has one, so the false
    models of Table 1 are fitted without intercepts as the paper writes them.
    Fitted probabilities are left unbounded; the paper does not trim weights.
    """
    X = dgps.design_matrix(data, spec["terms"])
    model = sm.GLM(data["D"].to_numpy(dtype=float), X,
                   family=sm.families.Binomial()).fit()
    return model.predict(X)


def estimate_ht(data, scenario, ps_spec):
    """Horvitz-Thompson estimate of the scenario's estimand."""
    propensity = fit_propensity(data, ps_spec)
    treatment = data["D"].to_numpy(dtype=float)
    n = len(data)

    if scenario == "A":
        outcome = data["Y"].fillna(0.0).to_numpy(dtype=float)
        return np.sum(treatment * outcome / propensity) / n

    outcome = data["Y"].to_numpy(dtype=float)
    treated = np.sum(treatment * outcome / propensity)
    control = np.sum((1.0 - treatment) * outcome / (1.0 - propensity))
    return (treated - control) / n


def estimate_or(data, scenario, or_spec):
    """Outcome-regression estimate: fit by OLS, then average fitted values."""
    terms = or_spec["terms"]

    if scenario == "A":
        observed = data["D"].to_numpy(dtype=float) == 1.0
        X = dgps.design_matrix(data, terms)
        coefficients = _ols(X[observed], data.loc[observed, "Y"].to_numpy(dtype=float))
        return float(np.mean(X @ coefficients))

    X = dgps.design_matrix(data, terms)
    coefficients = _ols(X, data["Y"].to_numpy(dtype=float))
    treated = dgps.design_matrix(dgps.with_treatment(data, 1), terms) @ coefficients
    control = dgps.design_matrix(dgps.with_treatment(data, 0), terms) @ coefficients
    return float(np.mean(treated - control))


def estimate_dr(data, scenario, ps_spec, or_spec, constrained=False):
    """Doubly robust estimate.

    The outcome-regression design is augmented with inverse-probability
    covariates and refitted by OLS; averaging the predictions then gives an
    estimate that stays consistent if either nuisance model is correct.

    Scenario A adds the single covariate 1 / pi(V).  Scenario B adds the two
    covariates D / pi(V) and (1 - D) / (1 - pi(V)) of Scharfstein et al.
    (1999), which is what reproduces Table 2.  With ``constrained=True`` the two
    coefficients are instead forced equal, the variant proposed in Section 2.2
    of the paper; the normal equation for the single coefficient then sets the
    sum of the two weighted residual terms to zero rather than each of them, so
    the resulting estimator is not doubly robust for the treatment effect.

    The augmenting covariates depend on the treatment received, so the
    counterfactual predictions must use their values at the treatment being
    predicted rather than at the observed one.
    """
    propensity = fit_propensity(data, ps_spec)
    terms = or_spec["terms"]

    if scenario == "A":
        observed = data["D"].to_numpy(dtype=float) == 1.0
        X = np.column_stack([dgps.design_matrix(data, terms), 1.0 / propensity])
        coefficients = _ols(X[observed], data.loc[observed, "Y"].to_numpy(dtype=float))
        return float(np.mean(X @ coefficients))

    treatment = data["D"].to_numpy(dtype=float)
    base = dgps.design_matrix(data, terms)
    base_treated = dgps.design_matrix(dgps.with_treatment(data, 1), terms)
    base_control = dgps.design_matrix(dgps.with_treatment(data, 0), terms)
    zero = np.zeros(len(data))

    if constrained:
        received = treatment * propensity + (1.0 - treatment) * (1.0 - propensity)
        augment = [1.0 / received]
        augment_treated = [1.0 / propensity]
        augment_control = [1.0 / (1.0 - propensity)]
    else:
        augment = [treatment / propensity, (1.0 - treatment) / (1.0 - propensity)]
        augment_treated = [1.0 / propensity, zero]
        augment_control = [zero, 1.0 / (1.0 - propensity)]

    X = np.column_stack([base] + augment)
    coefficients = _ols(X, data["Y"].to_numpy(dtype=float))
    treated = np.column_stack([base_treated] + augment_treated) @ coefficients
    control = np.column_stack([base_control] + augment_control) @ coefficients
    return float(np.mean(treated - control))


def estimate(data, scenario, family, ps_name, or_name):
    """Dispatch to the estimator named by ``family``, resolving model names
    against the scenario's specifications in ``config``."""
    spec = config.SCENARIOS[scenario]
    ps_spec = spec[ps_name] if ps_name else None
    or_spec = spec[or_name] if or_name else None

    if family == "ht":
        return estimate_ht(data, scenario, ps_spec)
    if family == "or":
        return estimate_or(data, scenario, or_spec)
    if family == "dr":
        return estimate_dr(data, scenario, ps_spec, or_spec)
    if family == "dr1":
        return estimate_dr(data, scenario, ps_spec, or_spec, constrained=True)
    raise ValueError(f"unknown estimator family: {family}")
