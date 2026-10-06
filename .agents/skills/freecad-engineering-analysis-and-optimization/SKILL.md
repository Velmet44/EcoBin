---
name: freecad-engineering-analysis-and-optimization
description: Plan, execute, verify, and document production mechanical engineering analyses and parametric optimization around FreeCAD models. Use whenever a user asks for hand calculations, load cases, strength/stiffness, heat transfer, modal response, buckling, fatigue, contact, FreeCAD FEM, CalculiX, Elmer, external solver handoff, mesh convergence, solver-result review, test correlation, sensitivity, DOE, Pareto tradeoffs, robust design, topology or dimensional optimization, or analysis evidence for design release. Solver output alone is never approval.
---

# FreeCAD Engineering Analysis and Optimization

Runtime compatibility: Codex and Claude Code; FreeCAD 1.1.2 is recommended for native FEM workflows. CalculiX, Elmer, meshers, or external solvers must be installed separately when the chosen analysis requires them.

Build an auditable argument that the design meets named requirements over controlled configurations and load cases. Treat simulation as one source of evidence: a plausible contour plot is not verification, validation, or release authorization.

## Establish authority and consequence

Require or mark unknown:

- Authoritative part/assembly, revision, configuration, parameter set, coordinate system, and geometry checksum.
- Functional requirements, acceptance limits, failure modes, service life, environment, duty cycle, and consequence category.
- Applicable standards and exact revisions; customer, regulatory, and organizational analysis rules.
- Design, limit, proof, ultimate, fatigue, abuse, shipping, assembly, and maintenance cases as applicable.
- Material specification, product form, condition, direction, temperature, lot variability, allowables basis, reductions, and joining data.
- Manufacturing tolerances, residual stress, preload, wear, corrosion, coating, damage, and credible imperfections.
- Analysis owner, independent reviewer, solver/version, model maturity, and release authority.

If failure can injure people, violate regulation, or cause major loss, route the work through the responsible licensed/authorized engineering organization. Do not invent safety factors or substitute simulation for required physical qualification.

Copy `assets/analysis-contract.template.json` for the machine-readable record and `assets/analysis-report.md` for the human review. Run:

```bash
python scripts/analysis_contract_validate.py path/to/analysis-contract.json
```

The validator checks evidence completeness and internal consistency; it does not establish that the physics or result is correct.

Its conservative default ceilings are 2% reaction imbalance, 20% analytical-comparison discrepancy, and 5% final mesh change. A project may use a looser limit only with a recorded technical justification, named approver, and approval date. Every quantity used by a release-driving result needs its own converged mesh study; convergence of benign displacement cannot qualify an unconverged governing stress.

## Build the load-case matrix before solving

Give every load case a stable ID and record:

| Case | Configuration | Event / duty | Loads and sources | Boundary state | Environment | Requirement | Combination rule |
|---|---|---|---|---|---|---|---|

Include direction and application distribution, not only magnitude. Trace gravity, acceleration, pressure, torque, thermal boundary, bolt preload, contact, installation strain, and externally supplied reactions to controlled evidence. Distinguish measured, calculated, requirement-derived, supplier-rated, and assumed values.

Separate service, proof, ultimate, fatigue-spectrum, fault, and transport cases. Define whether loads are simultaneous, mutually exclusive, enveloped, phased, or statistically combined. Never sum incompatible extrema without a defensible combination rule.

Use one declared coherent unit system per model and retain units on all imported/exported quantities. Check order of magnitude independently after every unit or coordinate transform.

## Calculate before discretizing

Create an analytical model where the physics permits:

- Free-body diagrams and equilibrium.
- Beam, shaft, plate, shell, pressure, bearing, joint, fastener, spring, thermal-resistance, or energy calculations.
- Bounding cases that deliberately over- and under-estimate response.
- Dimensional checks and independent order-of-magnitude estimates.

State assumptions and domains of validity. Compare analytical predictions with FEM at representative regions away from singularities. Investigate disagreement; do not tune unknown inputs merely to force agreement.

Read `references/verification-validation.md` for evidence grading and `references/fatigue-and-allowables.md` when life or material strength governs.
Read `references/dynamics-vibration-and-shock.md` for modal, harmonic, random, shock, transient and robot-load handoff requirements.

## Select physics and solver deliberately

Use `references/freecad-fem-and-solvers.md` to choose the implementation.

- Use CalculiX through FreeCAD FEM primarily for supported structural and thermomechanical work.
- Use Elmer through FreeCAD FEM for supported thermal, electromagnetic, flow, and coupled equations.
- Use an external solver when the required formulation, material model, contact, fracture, rotor dynamics, random vibration, fatigue, or qualification method is not adequately exposed or verified in FreeCAD.
- Use `../freecad-robot-motion-dynamics-and-validation/SKILL.md` for force-driven robot multibody/contact/actuator/control response. Transfer its verified interface loads into FEA with controlled frames, signs, units, time/event IDs and hashes.
- Record exported geometry/mesh hashes, solver decks, versions, options, conversion steps, and result files so the external handoff is reproducible.

Confirm that the selected solver, element, integration, nonlinear controls, and result recovery support the intended physics. A solver’s ability to run is not evidence that its formulation is appropriate.

## Idealize without changing the load path

Document every suppression, midsurface, beam, shell, symmetry, rigid region, remote load, bonded interface, lumped mass, connector, or submodel.

For each idealization, state:

1. What was changed.
2. Why its effect is negligible or conservative for the evaluated response.
3. What mass, stiffness, inertia, thermal path, contact, or load transfer it preserves.
4. How the assumption will be checked.

Avoid rigid constraints that create artificial stiffness, point loads that create nonphysical peaks, and symmetry where geometry, contact, load, material, or buckling mode breaks it.

## Define materials, interfaces, and boundary conditions

- Map each region to a controlled material record and product form.
- Separate typical properties from design allowables. Record statistical basis, temperature, direction, surface/process factors, weld/joint reductions, and source revision.
- Use temperature-dependent properties when the operating range makes them significant.
- Declare elastic/plastic, isotropic/orthotropic, linear/nonlinear, creep/viscoelastic, and damage assumptions.
- Give contacts a physical state: bonded, frictional, frictionless, separation, interference, thermal resistance, preload, or connector behavior.
- Apply constraints only where the real support transfers the corresponding reaction. Check sensitivity to uncertain stiffness, friction, preload, and support position.
- Include bolt pretension, joint slip, bearing load distribution, weld detail, adhesive cure, cable force, and seal compression where they materially affect the load path.

## Mesh to a quantity of interest

Declare element family/order, characteristic sizes, quality criteria, local refinements, contact discretization, and geometry association.

Run at least three systematically refined meshes for every release-driving quantity unless an approved alternative numerical verification method exists. Record degrees of freedom and the quantity at the same physical probe or integrated region. Demonstrate asymptotic behavior or explain why it is absent.

Converge displacement, reaction, strain energy, contact force, temperature/heat flow, eigenfrequency, or structural/hot-spot stress as appropriate. A re-entrant corner, point constraint, point load, contact edge, or ideal sharp crack may have non-convergent peak stress. Do not report that peak as a material demand; use a physically justified averaging, structural-stress, fracture, notch, or geometry-detail method and document it.

## Verify every run

Before interpreting acceptance:

- Check solver warnings, iterations, residuals, increments, stabilization, energy terms, and negative/invalid elements.
- Reconcile applied forces and moments against reactions in a common coordinate system.
- For thermal work, reconcile heat input, output, storage, and boundary flux.
- Check deformed shape and reaction directions against the free-body diagram.
- Compare mass, center of mass, stiffness, frequency, and thermal resistance with independent expectations.
- Confirm contact status, penetration, slip, preload, and load transfer.
- Review mesh convergence and sensitivity to boundary, material, contact, imperfection, and solver-control assumptions.
- Check result location and averaging. Preserve signed tensor/component results where the failure criterion needs them.

The contract requires a release-driving case to carry reaction/energy balance evidence, a convergence study, singularity disposition, and an analytical or benchmark comparison.

## Evaluate the required failure modes

### Static and nonlinear strength

Check deformation, stress/strain, stability, joint separation/slip, local bearing, fastener/weld/adhesive demand, plastic strain, and permanent set. Compare the right stress or strain measure with a compatible allowable. Include geometric and material nonlinearity when load path or stiffness changes materially.

### Thermal and thermomechanical

Check steady and transient extremes, power duty, convection/radiation/contact resistance, thermal expansion, gradients, distortion, preload loss, clearance change, and temperature-dependent properties. Correlate uncertain convection or interface conductance.

### Modal and dynamic

Check rigid-body modes, mass participation, frequency range, preload/contact state, boundary sensitivity, and mode-shape plausibility. A frequency margin alone does not predict response; use harmonic, transient, response-spectrum, shock, or random-vibration methods when excitation amplitude matters.

For release-driving response, require physics-specific verification: modal effective-mass/participation and extraction range; damping provenance; harmonic frequency resolution; random PSD units/integration/statistical peak basis; transient time-step/integrator sensitivity; shock pulse/SRS reconstruction; and energy/constraint checks appropriate to the method. Do not reuse a static mesh-convergence statement as proof that a transient, contact, modal, or fatigue quantity converged.

### Buckling

Use eigenvalue buckling only as screening. Release evidence for sensitive structures should include credible imperfections, nonlinear geometry, material response, contact, and residual stress as applicable. Report the imperfection basis and post-buckling acceptance.

### Fatigue and life

Use a controlled stress/strain history, cycle counting, mean-stress treatment, S-N or strain-life data, modifiers, notch method, cumulative-damage rule, scatter/reliability basis, and inspection/retirement assumptions. Do not apply an unmodified polished-specimen curve to a production joint.

## Validate against reality

Verification asks whether the equations were solved correctly; validation asks whether the equations and assumptions represent the intended use.

Plan coupon, subcomponent, modal-tap, thermal, strain-gauge, proof, endurance, or full-system tests at the fidelity required by consequence. Record instrumentation, calibration, setup stiffness, environmental conditions, uncertainty, and configuration.

Compare like-for-like observables with predeclared tolerances. When correlation is poor, identify whether geometry, material, boundary, contact, load, measurement, or numerics is responsible. Calibrate only physically uncertain parameters within justified bounds, preserve the pre-calibration prediction, and validate the updated model against independent data.

## Optimize only a verified model

Copy `assets/optimization-study.template.json` and read `references/optimization.md`.

The template returns `DRAFT`. A selection becomes a passing controlled study only
when its candidate resolves in the result table, every variable/objective/constraint
value is finite, constraints are feasible, objective deltas from the baseline are
explicit, robustness is quantified, and authoritative rebuild, fine-mesh,
analytical, and DFM confirmation evidence is hash- and configuration-bound.
Status strings alone cannot pass.

1. Freeze requirements and identify hard constraints, objectives, nuisance variables, and manufacturing bounds.
2. Choose stable FreeCAD parameters; prevent invalid topology and preserve interfaces, datums, minimum features, stock/process rules, and supplier envelopes.
3. Define baseline performance and verify the analysis at the baseline.
4. Use screening DOE or one-at-a-time checks only to detect implementation errors; use a suitable space-filling, factorial, response-surface, gradient, or evolutionary method for the actual problem.
5. Record random seeds, sample plan, failed designs, solver settings, and surrogate error.
6. Report sensitivities with ranges and interactions. Do not infer causality from a poorly sampled correlation.
7. Preserve the Pareto front for competing mass, stiffness, life, cost, thermal, and manufacturing objectives; do not hide the tradeoff inside arbitrary weights.
8. Add tolerance, load, material, and environmental variation. Evaluate probability/quantile or worst credible behavior at the required reliability.
9. Rebuild shortlisted designs from authoritative parameters and run independent, refined confirmation analyses.
10. Re-run DFM, assembly, tolerance, safety, and physical validation gates before release.

Never accept a surrogate prediction or coarse optimization mesh as final evidence.

## Decide and report

Use these evidence verdicts:

- `FAIL`: a requirement is violated, the model is invalid, or a release-critical check is missing.
- `CONDITIONAL`: no demonstrated violation, but a material assumption, test, convergence, correlation, or review action remains open.
- `PASS`: the named analysis case satisfies its acceptance criteria and its verification evidence is complete.

`PASS` applies only to the stated model, configuration, loads, requirements, and analysis scope. It does not authorize product release.

Complete `assets/analysis-report.md` with:

- Scope, configuration, requirements, load-case matrix, and exclusions.
- Methods, analytical estimates, assumptions, solver/version, and controlled inputs.
- Geometry idealizations, materials/allowables, contacts, boundary conditions, and mesh.
- Numerical checks, convergence, reaction/energy balance, and singularity dispositions.
- Results against criteria with margins and uncertainty.
- Validation/correlation evidence.
- Optimization trade space, robustness, Pareto candidates, and confirmation runs when applicable.
- Open actions, residual risks, verdict, independent review, and release-authority decision.

Archive the native model, solver decks, scripts, logs, results, plots with unambiguous legends/units, contract, report, and hashes. Never release from screenshots alone.
