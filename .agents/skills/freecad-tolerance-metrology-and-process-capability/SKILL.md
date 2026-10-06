---
name: freecad-tolerance-metrology-and-process-capability
description: Allocate and validate functional tolerances, fits, metrology, conformity decisions, and manufacturing capability for FreeCAD parts and assemblies. Use for CNC or additive tolerances, clearances, press/slip fits, GD&T/GPS, CTQs, inspection uncertainty, gauge R&R, Cp/Cpk/Pp/Ppk, supplier capability, compensation maps, first-article inspection, or any claim that a named process can repeatedly produce and inspect a feature.
---

# FreeCAD Tolerance, Metrology, and Process Capability

Runtime compatibility: Codex and Claude Code; Python 3.10+ for deterministic contract checks.

Turn functional requirements into a process- and state-specific tolerance scheme that can be manufactured, measured, and accepted. Never publish a universal “3D-printing tolerance,” infer part capability from machine positioning accuracy, or invent capability indices for a one-off part.

Use `../freecad-parametric-modeling/SKILL.md` for nominal geometry, `../freecad-assembly-engineering/SKILL.md` for tolerance stacks, `../freecad-dfm-review/SKILL.md` for route feasibility, and `../freecad-additive-manufacturing-engineering/SKILL.md` for qualified additive production. The nominal product model remains authoritative; shrink, warp, hole, or fit compensation belongs in a controlled manufacturing derivative or explicit parameter layer.

Read:

- `references/process-capability-and-metrology.md`
- `references/cnc-and-fit-capability.md`
- `references/additive-dimensional-capability.md`

Copy `assets/tolerance-capability-contract.json`, `assets/characteristic-capability-register.csv`, `assets/fit-and-interface-register.csv`, and `assets/measurement-system-register.csv`. Run `scripts/tolerance_capability_validate.py` before a production-candidate verdict.

## Gate 1 — Freeze the definition and process state

Record the part/revision/configuration, governing ISO GPS or ASME system, units, datum reference frame, temperature/conditioning, and acceptance authority. For every characteristic state whether it is inspected as-built, support-removed, stress-relieved, heat-treated, machined, coated, conditioned, or assembled.

Define the exact process tuple:

- Supplier and site; machine ID and controlled configuration.
- Process, material grade/batch, tooling or parameter-set revision.
- CNC setup/workholding/tool/thermal state, or AM orientation/build position/support/post-process state.
- Feature class and size range covered by evidence.

Capability evidence outside this envelope is not transferable without engineering justification and approval.

## Gate 2 — Allocate functional tolerances and fits

For each CTQ record function/failure prevented, nominal, LSL/USL, datum relationship, surface state, mating role, stack contribution, process operation, and measurement method. Use bilateral or unilateral limits intentionally. Separate clearance, transition, interference, sealing, alignment, bearing, threaded, adhesive, and compliant interfaces.

Use ISO 286 or the project’s controlled fit system only where its assumptions apply. Printed holes, pins, threads, snap fits, and press fits require measured process-specific characterization or a qualified insert/post-machining strategy. Include coating, temperature, moisture, creep, surface texture, form, and assembly force where they affect fit.

## Gate 3 — Establish representative capability

Use stable, representative production data. Record sample source, dates, quantity, rational subgrouping, distribution treatment, outlier policy, control-chart/stability evidence, and calculation method.

- Use `Cp/Cpk` only for a stable process with defensible within-process variation.
- Use `Pp/Ppk` to describe observed overall performance, not as proof of control.
- Handle unilateral limits and non-normal data with an approved method.
- Report confidence/uncertainty appropriate to sample size.
- For prototypes or one-off work, use qualified process evidence plus FAI or 100% CTQ inspection; do not fabricate capability indices.

Machine calibration, ISO 230 testing, or a vendor brochure can support the evidence chain but does not prove part capability for the actual geometry, material, setup, tool, and thermal state.

## Gate 4 — Qualify the measurement decision

For every CTQ record instrument, method, fixture, datum simulation, resolution, calibration status, environmental controls, accessibility, operator/program, and uncertainty. Perform gauge R&R or another suitable measurement-system study where repeated production decisions depend on it.

Define the conformity decision rule and guard band. Apply measurement uncertainty near specification limits; do not report a measured value as unconditionally conforming merely because its point estimate is inside the limits.

## Gate 5 — Control compensation and change

For AM or other compensated processes:

1. Build and measure representative artifacts/coupons across required orientations and build positions.
2. Preserve raw results and uncertainty.
3. Derive a versioned transform or feature-specific compensation with a bounded validity envelope.
4. Validate on independent parts/artifacts before and after compensation.
5. Keep nominal CAD separate and traceable to the manufacturing derivative.

Requalify after relevant machine maintenance/calibration, supplier/site/material/tooling/parameter changes, orientation or scale changes, post-process changes, prolonged drift, or failed monitoring.

## Gate 6 — Release and feedback

Tie CTQs to the drawing/model, control plan, FAI, sampling plan, nonconformance process, SPC where appropriate, and supplier approval. A production candidate requires:

- Complete scoped process and measurement records.
- Stable, representative evidence or an explicitly justified FAI/100% route.
- Approved conformity rule and uncertainty treatment.
- Qualified fits and controlled compensation.
- Owners, expiry/change triggers, and human approval.

Verdicts:

- `PASS — tolerance system production candidate`: the declared configuration has adequate scoped evidence; supplier/release authority remains identified.
- `DRAFT`: concept/prototype work without production capability evidence.
- `CONDITIONAL`: exact missing studies, assumptions, guard bands, or inspections are listed.
- `FAIL`: a CTQ cannot be produced, measured, accepted, or traced as declared.

The validator checks record completeness and selected arithmetic. It cannot prove process stability, measurement competence, supplier control, or physical conformance.
