"""Build the diagnostic and publication figures from the raw estimates."""


def plot_distributions(raw, out_path):
    """Diagnostic: sampling distribution of each estimator, faceted by
    scenario, with the true value marked."""
    raise NotImplementedError


def plot_bias_grid(summary, out_path):
    """Publication: bias with Monte Carlo error over the 2x2 grid of correct
    and false propensity and outcome-regression models."""
    raise NotImplementedError


def main():
    raise NotImplementedError


if __name__ == "__main__":
    main()
