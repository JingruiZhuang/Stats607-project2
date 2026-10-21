# Critical Analysis

Reproduction of Bang and Robins (2005), Table 2. Design in ADEMP.md.

## Reproduction

All sixteen cells reproduced, the largest gap from a published bias being 1.1 Monte Carlo standard
errors. Two parts of the description cannot be followed literally.

*The false propensity models need an intercept.* Table 1 lists only covariates for the two
deliberately wrong models, while others list theirs. Fitted literally, scenario A gives 0.47
against a published 0.69; with one, 0.6890.

*Table 2 does not use the estimator the paper recommends.* Section 2.2 proposes forcing the
coefficients on two inverse-probability terms to be equal. Implemented that way, the cell with a
correct propensity model and a false outcome model is biased by -2.59 rather than the published
-0.09; the earlier two-covariate estimator of Scharfstein et al. gives -0.073. That variant is not
doubly robust: robustness needs the difference of two weighted residual terms to vanish, and one
coefficient gives a single normal equation setting only their sum to zero. It is unbiased exactly
when the outcome model is correct, whatever the propensity model, which is ordinary outcome
regression.

## Neutrality of the design

The conditions are uniformly comfortable for the method promoted. Overlap is never stressed: in
scenario A the propensity score takes only two values, 0.269 and 0.5, so no weight exceeds 3.7,
and the instability that is weighting's main objection cannot arise. Misspecification is all-or-
nothing, while the paper's central argument concerns models that are merely nearly correct, never
tested though it is the practical case. The proposed estimator is never evaluated against the
predecessor it claims to improve on. Everything is at n = 500, and two-decimal reporting without
standard errors leaves rounding as large as the simulation error. I would add a mildly
misspecified condition and propensities near zero, vary the sample size, and evaluate the
estimator the paper recommends.

## Figures, surprises and confidence

The paper presents only tables, so I drew my own. The distribution figure shows what a table
cannot: with a false outcome model the doubly robust estimator keeps a similar box but far wider
outliers, so its cost is occasional badly wrong estimates, not a wider spread. The surprise was
that the published table does not match the method the text recommends; I hunted a bug in my own
code before trying the predecessor's.

I reproduced the cross-sectional scenarios, not the longitudinal results of Tables 3 and 4, and
did not simulate the extra conditions argued for, which is the next step. I am confident in the
sixteen cells: they agree on four measures, and the tests fail when the intercept decision is
reverted. For the constrained estimator the algebra, simulation and pattern across cells agree; I
cannot rule out a different reading of the formula.
