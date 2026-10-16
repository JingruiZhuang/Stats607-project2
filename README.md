# Doubly Robust Estimation: A Reproduction of Bang & Robins (2005)

A simulation study reproducing the cross-sectional results of Bang, H. and Robins, J. M. (2005),
"Doubly Robust Estimation in Missing Data and Causal Inference Models," *Biometrics* 61, 962-973.
Two scenarios are studied, a missing-data problem with estimand `E(Y)` and a treatment-effect
problem with estimand `E{Y(1)} - E{Y(0)}`, each with eight estimators formed by crossing the
Horvitz-Thompson, outcome-regression and doubly robust estimators with correct and
deliberately misspecified nuisance models. The design is documented in [ADEMP.md](ADEMP.md)
and the critical discussion in [ANALYSIS.md](ANALYSIS.md).

## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```
make all        # simulate, summarise, and build all figures
make simulate   # raw estimates  -> results/raw/estimates.csv
make analyze    # summary table  -> results/raw/summary.csv
make figures    # figures        -> results/figures/
make test       # test suite
make clean      # remove generated files
```

Estimated runtime: TBD.

## Key findings

TBD.

## Layout

```
src/config.py       simulation parameters and model specifications
src/dgps.py         data-generating mechanisms
src/methods.py      the estimators
src/metrics.py      performance measures
src/simulation.py   orchestration; writes raw estimates
src/analyze.py      raw estimates -> summary table
src/figures.py      figures
tests/              DGP, method, output and reproducibility checks
```
