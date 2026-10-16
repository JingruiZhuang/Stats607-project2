# ADEMP: Doubly Robust Estimation (Bang & Robins, 2005)

Reproduction of the cross-sectional simulations in Bang, H. and Robins, J. M. (2005), "Doubly
Robust Estimation in Missing Data and Causal Inference Models," *Biometrics* 61, 962-973.
Target results: Table 1A, Table 1B, and Table 2.

## Aims

1. Is the doubly robust (DR) estimator approximately unbiased whenever either the propensity
   model or the outcome regression (OR) model is correct, and biased only when both are wrong?
2. How much efficiency is lost by using DR in place of the correctly specified OR estimator,
   which is the MLE in these designs?

## Data-Generating Mechanisms

`V1, V2, V3` are independent `N(0, 1)`; `Il = 1(Vl > 0)`; `logit(r) = log{r / (1 - r)}`.
Sample size is `n = 500` with 1000 replicates per scenario.

### Scenario A: missing data

`Y` is observed only when `D = 1`; `V` is always observed.

- Outcome: `Y ~ N(s(V), 1)`, `s(V) = b . [1, V1^2, V2, V2*V3]`, `b = [0, 1, 2.5, 3]`.
- Missingness: `logit{pi(V)} = a . [1, I1, I2, I3, I1*I2]`, `a = [-1, 1, 0, 0, -1]`.
- False OR model: `Y` on `[1, V1, V2^2]`.
- False missingness model: `D` on `[1, I1, I3]`.

### Scenario B: treatment effect

`D` is a binary treatment. A fourth covariate `V4 ~ N(0, 1)`, independent of everything else,
is generated for use by the false treatment model only.

- Outcome: `Y ~ N(s(D, V), 1)`,
  `s(D, V) = b . [1, V1^2*D, V2*D, V2*V3*(1 - D), V3*(1 - D)]`, `b = [0, 2, 3, 2, -4]`.
- Treatment: `logit{pi(V)} = a . [1, I1, I2, I3, I1*I2]`, `a = [-3, 2.5, 3, 1, -3]`.
- False OR model: `Y` on `[1, V1*D, V2^2*(1 - D)]`.
- False treatment model: `D` on `[1, I3, V4]`, keeping one covariate that genuinely
  determines treatment and adding one noise covariate, as the text describes.

## Estimands

| Scenario | Estimand | True value |
| --- | --- | --- |
| A | `mu = E(Y)` | 1 |
| B | `mu = E{Y(1)} - E{Y(0)}` | 2 |

## Methods

All OR models use the identity link, fitted by OLS; propensity models are fitted by logistic
regression.

- **HT.** Scenario A: `n^-1 * sum{ D_i * Y_i / pi_i }`. Scenario B: difference of the
  arm-specific Horvitz-Thompson means.
- **OR.** Fit `s`, then average the fitted values (A) or the fitted contrast between `D = 1`
  and `D = 0` (B).
- **DR.** Add inverse-probability covariates to the OR design, refit by OLS, and average the
  predictions. Scenario A adds `1 / pi(V)`. Scenario B adds `D / pi(V)` and
  `(1 - D) / {1 - pi(V)}`, the two covariates of Scharfstein et al. (1999); the counterfactual
  predictions evaluate them at the treatment being predicted, not at the treatment received.

Four further cells, outside the reproduction grid, run the variant proposed in Section 2.2 of
the paper, which constrains the two augmentation coefficients to be equal and so adds the single
covariate `1 / f(D | V)` with `f(D | V) = D * pi(V) + (1 - D) * {1 - pi(V)}`. These are labelled
`DR1`, apply to scenario B only, and are reported separately. Scenario A adds a single
augmenting covariate whatever the constraint, so there the two variants are the same estimator.

Crossing the estimators with correct and false nuisance models gives the eight configurations of
Table 2: `HT`, `HT.fal`, `OR`, `OR.fal`, `DR`, `DR.ofal` (false OR), `DR.pfal` (false
propensity), `DR.o+pfal` (both false).

## Performance Measures

Over the 1000 replicates of each cell, with `mu` the true value and `m` the vector of estimates:

- Bias in mean: `mean(m) - mu`
- Bias in median: `median(m) - mu`
- Variance: sample variance of `m`
- IQR: 75th minus 25th percentile of `m`

Monte Carlo standard errors are reported alongside each measure, so that gaps between the
reproduction and the published values can be judged against simulation noise.

## Design Matrix

Sixteen cells: 2 scenarios by 8 estimator configurations, each at `n = 500` with 1000
replicates. Published values from Table 2 are the comparison targets. Four extension cells
(`DR1`, scenario B only) are run alongside and reported separately.

| Scenario | Estimator | Propensity | OR | Published bias | Published variance |
| --- | --- | --- | --- | --- | --- |
| A | `HT` | correct | - | -0.01 | 0.11 |
| A | `HT.fal` | false | - | -0.31 | 0.12 |
| A | `OR` | - | correct | 0.00 | 0.04 |
| A | `OR.fal` | - | false | -0.36 | 0.12 |
| A | `DR` | correct | correct | 0.00 | 0.04 |
| A | `DR.ofal` | correct | false | -0.02 | 0.11 |
| A | `DR.pfal` | false | correct | 0.00 | 0.04 |
| A | `DR.o+pfal` | false | false | -0.32 | 0.12 |
| B | `HT` | correct | - | -0.01 | 0.21 |
| B | `HT.fal` | false | - | 0.86 | 0.15 |
| B | `OR` | - | correct | 0.00 | 0.07 |
| B | `OR.fal` | - | false | -1.56 | 0.07 |
| B | `DR` | correct | correct | 0.00 | 0.09 |
| B | `DR.ofal` | correct | false | -0.09 | 0.28 |
| B | `DR.pfal` | false | correct | 0.00 | 0.08 |
| B | `DR.o+pfal` | false | false | 0.92 | 0.15 |

## Reproduction Procedure

1. For each replicate, draw a dataset of size 500 from the scenario's data-generating mechanism,
   using a seed derived deterministically from one master seed.
2. On that dataset fit the correct and false propensity models and the correct and false OR
   models, then compute all eight estimates. Estimators within a replicate share the same data,
   so comparisons across estimators are paired.
3. Write one row per estimate to a long-format file with columns
   `scenario, replicate, estimator, estimate`.
4. Summarise that file into the four performance measures and compare with the published values.

Two points of the published description are not literally reproducible and were resolved
numerically. The false propensity models of Table 1 are written without an intercept term, but
including one reproduces the published Horvitz-Thompson biases in both scenarios to two decimal
places while omitting one does not, so they are fitted with intercepts. The treatment-effect
results likewise match the two-covariate estimator of Scharfstein et al. rather than the
constrained variant that Section 2.2 proposes.

Propensity models use only `V`; `Y` enters only the OR models and the HT numerator. In scenario
A, OR models are fitted on complete cases (`D = 1`) and their predictions averaged over all `n`
subjects.
