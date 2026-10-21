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

Estimated runtime: about 22 seconds for `make all` on a laptop, of which 19 seconds is the
simulation itself; `make test` takes a further 9 seconds. Rerunning `make all` from clean
reproduces the committed figures byte for byte.

## Key findings

All sixteen cells of Table 2 reproduce, with the largest gap from a published bias being 1.1
Monte Carlo standard errors. Reaching that agreement needs two choices the paper does not
state: its deliberately wrong propensity models must be fitted with an intercept, and its
treatment-effect results come from the two-covariate estimator of Scharfstein et al. rather
than the constrained variant the paper itself proposes, which turns out not to be doubly
robust.

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

Outputs: `results/raw/estimates.csv` holds one row per estimate (20,000 rows),
`results/raw/summary.csv` one row per cell, and `results/figures/` the three figures.

## AI assistance

Course policy allows AI tools with attribution. This records where they were used.

Nothing in this repository predates the project. The following were drafted with Claude Code and
then reviewed, corrected and run by me:

| File | Role |
| --- | --- |
| `src/config.py` | parameters and the model specifications transcribed from Table 1 |
| `src/dgps.py` | the two data-generating mechanisms |
| `src/methods.py` | the Horvitz-Thompson, outcome-regression and doubly robust estimators |
| `src/metrics.py` | performance measures and their Monte Carlo standard errors |
| `src/simulation.py`, `src/analyze.py` | the simulation loop and the summary table |
| `src/figures.py` | the three figures |
| `tests/` | the test suite |
| `Makefile`, `requirements.txt` | workflow and dependencies |
| `ADEMP.md`, `ANALYSIS.md`, `README.md` | documentation |

The choice of paper, the scope of the reproduction and the reporting decisions were mine.

The two discrepancies reported in ANALYSIS.md, the intercepts in the false propensity models and
the estimator behind Table 2, were found by running the code against the published values rather
than taken from any source. Each is covered by a test that fails if the decision is reverted, so
both can be checked rather than taken on trust.
