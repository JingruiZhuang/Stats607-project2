# Critical Analysis

Reproduction of the cross-sectional simulations in Bang and Robins (2005), Table 2. Design and
procedure are in ADEMP.md; figures are in `results/figures/`.

## How well the results reproduced

All sixteen cells reproduced: the largest gap from a published bias is 1.1 Monte Carlo standard
errors, and the variances and interquartile ranges agree. But two parts of the description
cannot be followed literally, and each had to be settled by trying both readings.

**The false propensity models need an intercept.** Table 1 lists only covariates for the two
deliberately wrong propensity models, while other models in the same table list theirs. Fitted
literally, scenario A gives 0.47 against a published 0.69; with an intercept it gives 0.6890,
and scenario B moves from 1.75 to 2.8547 against a published 2.86.

**Table 2 does not use the estimator the paper recommends.** Section 2.2 proposes forcing the
coefficients on two inverse-probability terms to be equal, adding one covariate instead of two,
and calls this an improvement on Scharfstein et al. (1999). Implemented that way, the cell with
a correct propensity model and a false outcome model has a bias of -2.59 rather than the
published -0.09; the two-covariate version gives -0.073, which matches.

That variant is not doubly robust. Double robustness needs the difference of two weighted
residual terms to vanish: two coefficients give two normal equations setting each term to zero,
while one coefficient gives a single equation setting their sum to zero, leaving the difference
free. The simulation agrees, since the constrained estimator is unbiased whenever the outcome
model is correct and badly biased whenever it is not, regardless of the propensity model. That
is ordinary outcome regression, with no double robustness left.

## Was the simulation design neutral?

The sixteen cells support the conclusion drawn from them, but the conditions are uniformly
comfortable for the method being promoted.

**Overlap is never stressed.** In scenario A the propensity score takes only two values, 0.269
and 0.5, because two coefficients in the true model are zero, so no weight exceeds 3.7.
Scenario B is wider but still mild. Weighting estimators become unstable when propensities
approach zero, the main practical objection to them, and that cannot arise here.

**Misspecification is all-or-nothing.** The wrong models drop terms that genuinely matter and,
in scenario B, add a noise variable; no model is merely slightly wrong. Yet the paper's central
argument is about slight errors, that bias is small if either model is nearly correct. Since
every model in practice is somewhat wrong, the untested regime is the one that matters.

**The proposed estimator is never evaluated,** so the comparison a reader most wants, the new
estimator against the predecessor it claims to improve on, is absent. Running it would have
exposed the problem above.

**One sample size, coarse reporting.** Everything is at n = 500 with a linear outcome model, so
nothing separates small-sample from asymptotic behaviour. Values are given to two decimals with
no Monte Carlo standard errors; in the most precise cells that rounding contributes as much
uncertainty as the simulation, so a reader cannot tell a real discrepancy from a rounding one.

I would add a mildly misspecified condition, omitting one interaction rather than restructuring
the model; add propensities near zero; vary the sample size; and evaluate the estimator the
paper recommends.

## The figures

The paper presents only tables, so I drew my own. The distribution figure shows what a table
cannot: in scenario A the doubly robust estimator with a false outcome model has about the same
box as with a correct one but far wider outliers. The variance column records 0.113 against
0.042; the figure shows the cost is occasional badly wrong estimates rather than a uniformly
wider spread, which matters more to anyone using the method once on one dataset. The bias
figure puts each estimate and its Monte Carlo interval beside the published value and labels
each row with which models are correct, so the central claim is legible without decoding
estimator names.

## Surprises, limitations and confidence

The surprise was that the published table does not match the method the text recommends. I
implemented the paper as written, got a result I could not explain, and hunted a bug in my own
code before trying the predecessor's version, which matched at once. Only running it reveals
this. A smaller surprise was how cheap double robustness is here: in scenario A its variance is
0.0418 against 0.0416 for the maximum likelihood estimator.

I reproduced the two cross-sectional scenarios, not the longitudinal and marginal structural
model results of Tables 3 and 4. I also did not run the extra conditions argued for above, so
those criticisms rest on inspecting the design rather than simulating it, which is the next
step. I am confident in the sixteen cells: they agree on four measures at once, the tests check
them automatically, and restoring the literal intercept makes the test fail on exactly the
affected cell. I am about as confident about the constrained estimator, because the algebra
predicts the failure, the simulation shows it in the predicted place, and the pattern across
the four cells is what the algebra implies rather than merely large. What I cannot rule out
from the text alone is a different reading of the paper's formula than mine.

The hardest part was not the estimators but those two undocumented choices. A related trap is
that the augmenting covariate depends on the treatment received, so the predictions under
treatment and under control must each use their own value of it; reusing the observed value for
both yields an estimator that looks reasonable and quietly loses double robustness.
