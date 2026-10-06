---
name: freecad-parametric-modeling
description: Create or revise robust, editable, mechanically intentional FreeCAD parametric part definitions and regeneration scripts. Use for FreeCAD Part Design or Python modeling, FCStd generation, named parameters and expressions, fully constrained sketches, stable assembly datums/LCS, topological-naming resilience, design tables, families of parts, engineering calculations tied to geometry, or parameter-envelope testing for individually manufactured components.
---

# FreeCAD Parametric Modeling

Runtime compatibility: Codex and Claude Code; Python 3.10+ and FreeCAD 1.1.2/FreeCADCmd are required to execute model generation and runtime audits.

Use `../freecad-engineering-analysis-and-optimization/SKILL.md` whenever geometry acceptance depends on strength, stiffness, buckling, fatigue, modal, thermal, contact, impact, or optimization claims. This skill owns robust geometry and parameterization; it does not turn a recomputable solid into verified engineering performance.

Build a model that communicates design intent, regenerates across its approved parameter envelope, and remains editable by another designer. Geometric validity is necessary but does not establish strength, tolerance compliance, or manufacturability.

Prefer FreeCAD 1.1.2 or a user-pinned version. Record `App.Version()` and OpenCASCADE version in the build report.

## Inputs

Start from a completed production brief or create one from `assets/part-input.json`. Do not invent a safety-critical load, material, interface, fit, tolerance, or process limit.

Before modeling, establish:

- Coordinate system, origin, functional datum reference frame, and positive build/tool directions.
- Required solids/bodies, assembly context, master geometry, symmetry, and configuration boundaries.
- Named parameters with value, unit, meaning, source, allowed range, and whether they are independent, derived, reference-only, or supplier-controlled.
- Critical interfaces, keep-in/keep-out volumes, stock allowance, finish/coating allowance, and inspection access.
- Stable assembly interface IDs/datums, controlled mass/material properties, and which geometry is authoritative versus reference/envelope.
- Equations and external analyses that drive dimensions.

Read `references/robust-modeling.md` before creating a feature tree. Read `references/freecad-scripting.md` before writing a generator.

## Choose the representation

- Use one `PartDesign::Body` per contiguous manufactured solid. Keep `Allow Compound` off unless multiple solids are intentional and downstream tools accept them.
- Use multiple Bodies for physically separate solids, alternative manufacturing stages, or controlled master/tool geometry.
- Use `Std Part` for grouping/placement, not as a substitute for a Body.
- Keep released part definitions independently auditable. Use `../freecad-assembly-engineering/SKILL.md` for mating, occurrences, kinematics, BOMs, assembly-only envelopes, and exploded views.
- Use `../freecad-component-sourcing/SKILL.md` rather than remodeling or casually downloading standard/purchased hardware, servos, boards, or supplier parts.
- Use a Spreadsheet or dedicated property object as the input layer. Use a separate reporting sheet for model-derived values to avoid cyclic dependencies.
- Prefer a scripted generator when the result must be reproducible at scale, produced without GUI interaction, or versioned as text. Still save the native FCStd result.

## Model in this order

1. Create the document, metadata, units, and parameter layer.
2. Establish the Body origin, datums, master sketches, construction geometry, interface skeletons, and keep-out references.
3. Create the primary stock/envelope feature.
4. Add major functional material and primary interfaces.
5. Add cuts, holes, slots, patterns, and repeated features from named references.
6. Add manufacturing relief, standard tool radii, draft, or bend features after the selected process is known.
7. Add edge breaks, chamfers, and fillets late; separate functional radii from cosmetic edge treatment.
8. Create reporting properties, TechDraw references, and release exports only after geometry stabilizes.

Do not put assembly-only adaptive cuts into a reusable master part, edit a purchased component to make the assembly fit, or fuse separate occurrences into one Body. If a real secondary machining operation creates a unique installed item, give it a controlled derived part number/revision and manufacturing definition.

Name features for intent, such as `bearing_seat`, `mount_pattern`, and `deburr_0p3`, not `Pad003`.

## Sketch and reference rules

- Fully constrain every production sketch. Permit an under-constrained sketch only when the remaining degree of freedom is intentional, documented, and bounded.
- For a scripted direct-B-rep model with no sketches, replace the sketch gate with explicit input-range checks, named constructive features, deterministic rebuild, final-shape/BOP checks, and semantic measurements of every critical interface. The absence of sketches is not itself a failure.
- Constrain design intent with symmetry, equality, tangency, construction geometry, and named dimensions. Avoid solving the sketch by fixing arbitrary coordinates.
- Keep sketches small and functionally coherent; split unrelated profiles.
- Attach sketches and datums to Body origin planes/axes or stable datum geometry whenever possible.
- Prefer master sketches, carbon copies, named constraints, and SubShapeBinders over generated face/edge references.
- Do not use `Face12` or `Edge37` as an enduring design identifier. If a feature must reference generated topology, isolate the dependency, test it across the parameter envelope, and document the repair strategy.
- Avoid cross-body links that produce out-of-scope dependencies. Use a ShapeBinder/SubShapeBinder and verify relative placement.
- Inspect the dependency graph for cycles, red out-of-scope links, and unexpected branches.
- Expose durable datums/LCS for assembly mates at functional, inspectable interfaces; do not require downstream assemblies to mate to generated topology.

## Parameter and equation rules

- Use explicit unit-bearing values: `12 mm`, `35 deg`, `0.5 kg`, not bare numbers where a quantity is expected.
- Give spreadsheet aliases and constraint names descriptive multi-character identifiers; avoid short tokens that collide with units.
- Maintain one source of truth. Derive repeated dimensions with expressions.
- Preserve exact design equations in the model or calculation record; do not replace them with rounded constants.
- Apply rounding only at the requirement boundary and state the direction/rationale.
- Store nominal geometry as nominal. Put tolerances, material condition, surface texture, and process notes in product definition unless a deliberate worst-case or tooling model is being built.
- Model coating/plating, stock, shrink, springback, cutter compensation, or print compensation only when the workflow explicitly assigns that responsibility to CAD. Otherwise record it as process metadata.

## Mechanical design checks

Perform calculations that the part’s function requires. At minimum consider:

- Static strength, stiffness/deflection, buckling, bearing, shear-out, tear-out, thread stripping, fastener preload/slip, fatigue, wear, thermal growth, creep, and impact as applicable.
- Fits and clearances at material and thermal extremes.
- Tolerance stacks through assembly interfaces.
- Assembly installation/tool/cable envelopes and occurrence-level checks are handed to the assembly skill; retain the part-side datum, tolerance, coating, and interface evidence needed by that analysis.
- Stress concentration at holes, shoulders, grooves, threads, and sharp transitions.
- Load path continuity and realistic boundary conditions.
- Material allowables for the actual condition, direction, temperature, process, and life.

Record assumptions and require qualified review for high-consequence applications. Do not claim a factor of safety from nominal CAD dimensions alone.

## Regeneration and envelope validation

At each logical phase:

1. Recompute.
2. Fail on document/object error states.
3. Confirm the expected solid count.
4. Confirm the final shape is non-null, valid, closed where applicable, and has positive volume.
5. Check mass properties and envelope against independent expectations.

Test nominal plus meaningful boundary and interaction cases:

- Every independent parameter at minimum and maximum.
- Combinations likely to cause zero thickness, coincident/tangent transitions, lost intersections, pattern overlap, tiny edges, or feature inversion.
- Fit/clearance and stock/process extremes.

Use `../freecad-release-validation/scripts/freecad_parameter_sweep.py` with
FreeCADCmd for scripted checks; follow the invocation and case schema in the
release-validation skill. A passing nominal case is not evidence of parametric
robustness.

## Scripting contract

When generating through Python:

- Make inputs data, not scattered literals.
- Validate units, ranges, and cross-parameter inequalities before geometry.
- Use stable internal names and human-readable labels.
- Recompute after logical groups and raise a clear error immediately.
- Keep GUI-only code out of headless build paths.
- Do not catch and discard FreeCAD exceptions.
- Save only after assertions pass.
- Emit a machine-readable build report containing input values, software versions, target objects, mass properties, and checks.
- Make the generator deterministic for the same inputs and version; document any kernel-sensitive operations.

Use `scripts/freecad_build_contract.py` as a reusable starting module.

## Deliverables

Return:

- Native FCStd and, when scripted, the generator plus exact input data.
- Parameter table with units, ranges, provenance, and dependency type.
- Design-intent / feature map.
- Calculation references and unresolved assumptions.
- Nominal and envelope audit results.
- Screenshots or views that expose datums, critical interfaces, and feature tree when useful.
- Controlled material/density or explicitly sourced mass plus named assembly datums/LCS and interface identifiers.

Label the result `concept`, `prototype`, or `production candidate`; do not call it released.
