# DOE, sensitivity, and robust optimization

Use this reference when exploring more than a few design variants or making an optimum a release candidate.

## Formulate

Define:

- Decision variables with units, bounds, manufacturing resolution, dependency, and valid topology.
- Fixed parameters and noise variables with justified ranges/distributions/correlation.
- Objective directions and normalization.
- Hard constraints linked to requirements and soft preferences kept separate.
- Infeasible-geometry, solver-failure, and missing-result handling.
- Baseline and reference design.

## Sample and learn

- Use factorial/fractional designs for small structured spaces and interactions.
- Use Latin-hypercube or other space-filling designs for continuous global exploration.
- Use gradients only after checking smoothness and derivative accuracy.
- Use response surfaces or Gaussian-process/surrogate models only with cross-validation and reserved confirmation points.
- Record seed, sampler version, samples requested/completed/failed, solver settings, mesh policy, runtime, and extracted outputs.

Plot main effects and interactions over declared ranges. Report standardized or physically scaled sensitivity; avoid ranking variables whose ranges were chosen arbitrarily.

## Decide

For multiple objectives, show the non-dominated/Pareto candidates. Record why a candidate was selected and how much objective performance is traded for robustness, cost, or manufacturability.

Evaluate tolerance, material, load, boundary, and environmental variation on shortlisted candidates. Match Monte Carlo, polynomial chaos, worst-case, interval, or reliability methods to the evidence quality and tail consequence. A small random sample cannot substantiate a rare-failure probability.

## Confirm

Rebuild selected candidates using authoritative CAD parameters. Run:

- Geometry/recompute and manufacturability checks.
- Independent fine-mesh solution and analytical/equilibrium checks.
- Worst credible and statistical robustness cases.
- Tests or correlation required by consequence.

Optimization changes the design evidence baseline. Re-run affected requirements and release checks; never inherit a baseline approval automatically.
