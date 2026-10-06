# Verification, validation, and correlation

Use this reference to grade evidence and plan independent checks.

## Evidence ladder

1. **Input verification** — revision, units, coordinates, geometry, mass, materials, loads, and boundary conditions match their sources.
2. **Code verification** — the solver/formulation is benchmarked for the selected physics.
3. **Calculation verification** — equilibrium, energy, iterations, discretization error, sensitivity, and numerical settings are acceptable.
4. **Solution comparison** — analytical/bounding solutions or an independently implemented model agree where their assumptions overlap.
5. **Validation** — physical measurements agree with predicted observables over the intended domain with uncertainty considered.
6. **Qualification/acceptance** — the controlling authority accepts the prescribed evidence. This is not implied by the earlier steps.

## Minimum release-driving record

- Free-body diagram and load/constraint traceability.
- Solver and mesher logs without unresolved material warnings.
- Force and moment reaction balance with a project-defined tolerance.
- Thermal energy balance when applicable.
- At least three mesh levels for each critical quantity, or an approved alternative.
- Result trend versus characteristic size/DOF and a declared discretization acceptance.
- Singularity list and a physically meaningful stress/result extraction method.
- Analytical, handbook, benchmark, or independent-model comparison.
- Sensitivity to uncertain material, load, support, contact, imperfection, and damping inputs.
- Independent review and disposition of every discrepancy.

Do not universalize the example numerical tolerances bundled in the template. Set them from consequence, requirement margin, model behavior, and controlling procedures.

The bundled validator fails closed above its conservative default ceilings: 2% reaction imbalance, 20% analytical-comparison discrepancy, and 5% final mesh change. A looser project limit requires `acceptance_limit_justifications` evidence with a technical justification, approver, and ISO approval date. Use a separate `mesh_convergence` study for every release-driving result quantity; one flat level list remains valid for a single-quantity case.

## Test correlation

Pre-register:

- Test article revision/configuration and deviations from the analysis model.
- Sensor type, position, orientation, sampling, filtering, calibration, and uncertainty.
- Fixture/support stiffness and measured inputs.
- Compared observables, time/frequency alignment, and acceptance bands.

Report absolute and relative discrepancy with measurement and model uncertainty. Preserve raw data and the original prediction. Calibration data and validation data should be independent.

## Primary sources

- NASA Langley Research Center Procedure LPR 1710.15K, *Facility Safety Analysis*: requires closed-form/equilibrium/boundary checks and convergence evidence for finite-element validation: https://lmse.larc.nasa.gov/admin/public_docs/LPR_1710-15K_Final.pdf
- NASA NPARC Alliance, *Verification and Validation Documentation Guidelines*: https://www.grc.nasa.gov/www/wind/valid/document.html
- NIST, *Uncertainty of Measurement Results*: https://www.nist.gov/pml/nist-technical-note-1297

Use the project’s controlling V&V, certification, and uncertainty procedures where they are more restrictive.
