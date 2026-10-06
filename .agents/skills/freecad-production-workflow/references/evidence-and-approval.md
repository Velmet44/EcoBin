# Evidence and approval policy

## Purpose

Separate deterministic checks, engineering judgment, supplier capability, and organizational authorization. A production release needs all applicable layers.

## Evidence classes

1. **Computed** — CAD dimensions, mass properties, geometry validity, parameter-sweep results, toolpath extents, or checksums produced from named inputs and software versions.
2. **Specified** — controlled material, process, dimensional, surface, thread, regulatory, or customer requirements.
3. **Analyzed** — tolerance stacks, hand calculations, FEA, fatigue, thermal, flow, mold-fill, forming, or process simulations with documented assumptions and correlation limits.
4. **Confirmed** — supplier capability, available tooling, machine/controller behavior, postprocessor output, gauge availability, or material certification.
5. **Approved** — signed design review, manufacturing review, quality review, deviation, or release authorization.

Never present one class as another. For example, a valid B-rep is computed evidence, not proof that a wall can be machined without deflection.

## Claim rules

- Use `verified` only for a named requirement with a reproducible check and result.
- Use `validated` only when the result has been shown to satisfy intended use under defined conditions.
- Use `manufacturable` only relative to a named process, supplier/machine envelope, and accepted assumptions.
- Use `machine-ready G-code` only after controller-specific post verification and authorized shop prove-out.
- Use `compliant` only with the exact standard revision, scope, evidence, and approving authority.

## Unknowns register

Record:

| ID | Unknown / assumption | Why it matters | Current value | Evidence needed | Owner | Due gate |
|---|---|---|---|---|---|---|

Block release when an unknown can alter safety, regulatory compliance, interchangeability, critical fit, load capacity, material state, process route, inspection feasibility, or machine safety.

## Human approval boundaries

Require qualified human review for:

- Safety factors, code/regulatory interpretation, fatigue/fracture, pressure containment, lifting, guarding, medical/aerospace/automotive controls, and other high-consequence uses.
- GD&T scheme and tolerance-stack acceptance.
- Material/process substitutions, heat treatment, welding/brazing, coating, special processes, and supplier deviations.
- CAM feeds/speeds, workholding, collision clearance, postprocessor output, and machine prove-out.
- Final drawing and change-control release.

## Change control

Any change to geometry, parameter values, material, process, finish, supplier, machine, postprocessor, or acceptance criteria invalidates the affected evidence. Re-run dependent gates and issue a new revision; do not overwrite a released package.
