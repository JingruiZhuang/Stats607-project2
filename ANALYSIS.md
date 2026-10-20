# Critical Analysis

Reproduction of the cross-sectional simulations in Bang and Robins (2005), Table 2.
Design and procedure are in [ADEMP.md](ADEMP.md); figures are in `results/figures/`.

## How well the results reproduced

All sixteen cells reproduced. Across them the largest gap from the published bias is 1.1 Monte
Carlo standard errors, and the variances and interquartile ranges agree as well. The paper's
numbers are correct.

Two parts of the description cannot be followed literally. Both had to be settled by trying each
option and seeing which reproduced the published numbers.

**The false propensity models need an intercept.** Table 1 lists the variables in each model.
For the two deliberately wrong propensity models it lists only covariates, with no constant
term, while other models in the same table list theirs. Fitted literally, scenario A gives a
Horvitz-Thompson estimate of 0.47 against a published 0.69. With an intercept it gives 0.6890,
and scenario B moves from 1.75 to 2.8547 against a published 2.86. Both scenarios land on the
published value at once, so the models were fitted with intercepts.

**Table 2 does not use the estimator the paper recommends.** Section 2.2 proposes forcing the
coefficients on two inverse-probability terms to be equal, adding one covariate instead of two,
and says this improves on the earlier estimator of Scharfstein et al. (1999). Implemented that
way, the cell with a correct propensity model and a false outcome model has a bias of -2.59
instead of the published -0.09. The two-covariate version gives -0.073, which matches. The
published treatment-effect results therefore come from the predecessor's estimator, not from
the one the paper puts forward.

This is not a rounding issue. The constrained version is not doubly robust, and the reason is
visible in the estimating equations. Double robustness requires the difference of two weighted
residual terms to vanish. With two coefficients, least squares sets each term to zero
separately, so the difference vanishes. With one coefficient there is a single equation setting
their sum to zero, and the difference can be anything. The simulation matches: the constrained
estimator is unbiased whenever the outcome model is correct and badly biased whenever it is
not, regardless of the propensity model. That is the behaviour of an ordinary outcome
regression, with no double robustness left.

## Was the simulation design neutral?

The design is honest about what it sets out to show, and the sixteen cells support the
conclusion drawn from them. But the conditions are uniformly comfortable for the method being
promoted.

**Overlap is never stressed.** In scenario A the propensity score takes only two values, 0.269
and 0.5, because two of the five coefficients in the true model are zero. No subject can
receive a weight above 3.7. Scenario B is wider but still mild, with a smallest propensity near
0.05. Weighting estimators become unstable when some propensities approach zero, and that is
the main practical objection to them. It cannot arise anywhere in this design.

**Misspecification is all-or-nothing.** The wrong models drop terms that genuinely matter and,
in scenario B, add a pure noise variable. No model is merely slightly wrong. Yet the paper's
central argument for routine use is about slight errors: if either model is nearly correct, the
bias will be small. That claim is never tested, and since every model in practice is somewhat
wrong, the untested regime is the one that matters.

**The proposed estimator is never evaluated.** No table reports the constrained variant. The
comparison a reader most wants, the new estimator against the predecessor it claims to improve
on, is absent. Running it would have exposed the problem above immediately.

**One sample size, one link.** Everything is at n = 500 with a linear outcome model. Nothing in
the results separates a small-sample effect from an asymptotic one.

**Reported precision is too coarse to check.** Values are given to two decimals with no Monte
Carlo standard errors. Across the sixteen cells the standard error of a bias runs from 0.006 to
0.017 and of a variance from 0.002 to 0.013, so in the most precise cells the rounding of the
published value contributes as much uncertainty as the simulation itself. For those cells a
reader cannot distinguish a real discrepancy from a rounding difference.

## What I would change

Add a mildly misspecified condition, omitting one interaction rather than restructuring the
model, to test the paper's actual argument. Add a condition with propensities near zero. Vary
the sample size. Report standard errors and more decimals. Evaluate the estimator the paper
recommends.

## The figures

The paper presents only tables, so I drew my own.

The distribution figure shows what a table cannot. In scenario A the doubly robust estimator
with a false outcome model has about the same box as with a correct one, but far wider
outliers. The variance column records 0.113 against 0.042; the figure shows the cost is not a
uniformly wider spread but occasional badly wrong estimates. For anyone using the method once
on one dataset, that distinction matters more than the variance.

The bias figure places each estimate and its Monte Carlo interval beside the published value,
so the quality of the reproduction can be read directly. Labelling each row with which models
are correct makes the central claim legible without decoding estimator names. The third figure
shows a comparison the paper never makes, between the constrained variant and the estimator
Table 2 used.

## Surprises, limitations and confidence

The surprise was that the published table does not match the method the text recommends. I
implemented the paper as written, got a result wrong by a factor I could not explain, and spent
some time hunting a bug in my own code before trying the predecessor's version, which matched
at once. Reading the paper gives no hint of this; only running it does. A smaller surprise was
how cheap double robustness is here: in scenario A, with a correct outcome model, its variance
is 0.0418 against 0.0416 for the maximum likelihood estimator, a difference well inside Monte
Carlo error. That part of the argument holds up well.

I reproduced the two cross-sectional scenarios, not the longitudinal and marginal structural
model results of Tables 3 and 4, which use a more involved sequential procedure; nothing here
speaks to those. I also did not run the extra conditions I argue for, so the overlap and mild
misspecification criticisms rest on inspecting the design rather than simulating it. Simulating
them is the obvious next step.

I am confident in the sixteen reproduced cells: they agree on four measures at once, the tests
check them automatically, and restoring the literal reading of the intercept makes the test
fail on exactly the affected cell, so the check has teeth. I am about as confident in the
finding about the constrained estimator, for a different reason. Three lines agree: the algebra
predicts the failure, the simulation shows it in the predicted place, and the pattern across
the four cells is what the algebra implies rather than merely large. The one thing I cannot
rule out from the text alone is a different reading of the paper's formula than mine.

The hardest part was not the estimators but those two undocumented choices. A related trap is
that the augmenting covariate depends on the treatment received, so the predicted outcomes
under treatment and under control must each use their own value of it. Reusing the observed
value for both yields an estimator that still looks reasonable and quietly loses double
robustness, the same failure as the constrained variant and easy to ship unnoticed.
