---
name: freecad-release-validation
description: Audit, verify, and package FreeCAD parts, robots, additive builds, and assemblies for controlled manufacturing release. Use for FCStd validation, parameter/configuration sweeps, component/BOM/joint checks, FEA and robot-dynamics credibility, tolerance/process capability, metrology, AM qualification, animation/exploded work-instruction traceability, reliability, production routing, STEP reimport, TechDraw review, manifests/checksums, revision impact, or production-candidate signoff.
---

# FreeCAD Release Validation

Runtime compatibility: Codex and Claude Code; Python 3.10+ for manifests and FreeCAD 1.1.2/FreeCADCmd for model, sweep, and exchange-file audits.

Build an evidence-backed release candidate. Automated checks catch deterministic defects; they do not replace design, manufacturing, quality, standards, or safety approval.

Target FreeCAD 1.1.2 unless pinned. Record FreeCAD, OpenCASCADE, workbench/add-on, postprocessor, and helper-script revisions used.

Read:

- `references/cad-audit.md` for native geometry and parameter validation.
- `references/drawings-and-exchange.md` for TechDraw, STEP, DXF, and mesh release.
- `references/revision-and-inspection.md` for CTQs, manifests, approvals, and change impact.

## Gate 1 — Freeze the review basis

Identify:

- Part number/name, revision, maturity, owner, and approving functions.
- Product level, configuration/effectivity, authoritative root assembly when applicable, and exact child definition revisions/hashes.
- Authoritative native file and regeneration script/input data.
- Material/process/finish, units, projection, governing standards and revisions.
- Critical interfaces, datum scheme, CTQs, tolerance stack, scoped process-capability and metrology contract, calculations, DFM, CAM, and inspection plan.
- Supplier/machine and process capability evidence.
- Required release file types and recipient expectations.
- Component provenance/use-rights records, BOM, joint/DOF plan, interface/tolerance analysis, assembly/service sequence, and physical acceptance plan when applicable.
- Analysis/load-case/allowable/convergence/correlation evidence, production BOM views, router/cost/yield records, robotics verification, and reliability-risk closure when applicable.

Do not overwrite a previously approved revision. Work in a new controlled revision.

## Gate 2 — Audit the native model

Run `scripts/freecad_model_audit.py` in `FreeCADCmd`, targeting the released Body/solid. Require:

- Successful recompute with no invalid/error object state.
- Expected target objects and solid count.
- Non-null, valid, closed positive-volume shape.
- Plausible volume, area, bounding box, and center of mass.
- Production sketches solved and fully constrained, or each exception dispositioned.
- No unintended compounds, shells, duplicate visible release solids, out-of-scope links, or dependency cycles.

Also run GUI Part → Check Geometry on the complete final part with BOP check enabled. Save the result. FreeCAD does not automatically repair geometry; fix the generating feature.

For assemblies, invoke `../freecad-assembly-engineering/SKILL.md` and additionally require:

- Root/child links resolve to exact controlled revisions; no missing, circular, or stale references.
- Unique occurrence IDs, expected recursive occurrence counts, configuration effectivity, and controlled BOM reconciliation.
- Intended ground, successful cold solve, resolved joints, declared DOF/limits, and rigid/flexible subassembly behavior.
- Governed component records for standard/buy/ECAD items and no release dependence on unverified reference geometry.

The part audit scripts do not provide these assembly claims.

Invoke the companion owner skill rather than accepting a document title as evidence:

- `../freecad-engineering-analysis-and-optimization/SKILL.md` for calculation, FEM, convergence, V&V, DOE, and optimization claims.
- `../freecad-production-bom-and-configuration/SKILL.md` for released BOM views, effectivity, as-built traceability, and where-used.
- `../freecad-manufacturing-planning-and-material-optimization/SKILL.md` for routers, cost, yield, nesting/cut/build utilization, and waste.
- `../freecad-tolerance-metrology-and-process-capability/SKILL.md` for CTQ/fit capability, uncertainty, decision rules, compensation and supplier approval.
- `../freecad-additive-manufacturing-engineering/SKILL.md` for AM process/coupon/post-process/inspection/build-data qualification.
- `../freecad-robot-motion-dynamics-and-validation/SKILL.md` for multibody/controls model verification and physical correlation.
- `../freecad-assembly-visualization-and-work-instructions/SKILL.md` for traceable frames/media, exploded TechDraw, manuals and visual QA.
- `../freecad-robotics-mechanism-engineering/SKILL.md` for powered-mechanism sizing, frames, accuracy, safe states, and performance tests.
- `../freecad-reliability-and-risk/SKILL.md` for failure/risk records, action closure, and residual-risk approval.

## Gate 3 — Validate the parameter envelope

Run `scripts/freecad_parameter_sweep.py` against nominal, lower/upper limits, and interaction cases. Include cases likely to create:

- Zero/negative wall or ligament.
- Lost intersection, tangent/coplanar Boolean, or separated solid.
- Feature/pattern overlap or inversion.
- Fillet/chamfer failure or tiny edges.
- Fit/clearance violation.
- Tool/process access failure.

For each case require successful recompute, expected solid count, valid shape, and expected envelope/property checks. Visually inspect topology-changing cases. Restore and independently re-audit nominal.

For assemblies, enumerate released configurations and required mechanism poses. Check joint/DOF state, non-allowlisted solid intersections, required minimum distances, swept motion, stops, cable/tool/service envelopes, and worst-case fit margins. State sampling/refinement limits; a finite animation frame set does not prove continuous collision freedom.

Define what “all configurations” means:

- For a finite approved set, enumerate every member, mark coverage `finite_exhaustive`, and declare the exact release-case names. The report returns `FINITE_EXHAUSTIVE_PASS` only when that declared set and every critical assertion pass.
- For integer/stepped or continuous spaces that are not completely enumerated, mark coverage `sampled`, record the method, seed, domain, and limitations. The report returns `SAMPLED_PASS`, never an exhaustive claim.
- Keep deliberately invalid cases as `negative_regression`; they test failure behavior but do not count as released configurations.

## Gate 4 — Review product definition

Check the controlled drawing/model definition:

- Exact standard system and revision; no accidental ASME/ISO mixing.
- Correct units, projection symbol, scale, title block, part/revision, material/condition, finish/coating, mass if controlled, and general tolerance.
- Complete functional dimensions without duplicates or contradictions.
- Datum reference frame based on inspectable functional features.
- GD&T and material-condition modifiers that express actual assembly/function.
- Thread, hole depth, edge, surface texture, heat treatment, coating, marking, and special-process notes.
- CTQs mapped to an inspection method, datum simulation, sampling/FAI, and post-process state.
- Reference dimensions clearly marked and not used for acceptance.

TechDraw dimensions can break or change attachment after topology edits. Recheck every dimension and annotation after model regeneration; do not trust a visually populated page automatically.

## Gate 5 — Verify exchange artifacts

For STEP or another B-rep exchange:

1. Export only intended final objects.
2. Record schema/options, units, application/version, and checksum.
3. Open/import into a clean document.
4. Recompute and run geometry/BOP checks.
5. Compare solid count, volume, area, bounding box, placement, and selected critical geometry against native data with project-defined tolerances.
6. Confirm assembly/part names, colors/metadata where contractually required.

For an assembly, verify hierarchy and occurrence identity survive to the contractual extent; STEP geometry does not preserve FreeCAD joints, motion, exploded states, BOM authority, or ECAD manufacturing data.

For DXF, confirm plane, units, closed profiles, layers, duplicate/overlapping entities, arcs/splines, and flat-pattern responsibility.

For STL/3MF, define linear/angular deflection from the allowed chordal error, verify units/orientation, manifold/watertight mesh, normals, components, wall/features, and reimport envelope. Never use STL as the authoritative precision model when B-rep is required.

## Gate 6 — Verify manufacturing and inspection evidence

- Close all BLOCKER/MAJOR DFM findings or attach approved deviations.
- Confirm engineering calculations and CAE results meet their declared verification, convergence, uncertainty, allowable, and validation gates.
- Confirm the drawing tolerance/finish is compatible with selected process and post-processes.
- Confirm every production CTQ resolves to the exact process state, scoped capability or justified FAI/100% inspection, measurement system, uncertainty, decision rule, control plan, change trigger, and approval.
- For additive routes, confirm the exact process tuple, state chain, artifacts/coupons, material basis, compensation derivative, cleaning, post-processing, inspection, build/lot record, and requalification triggers.
- Confirm critical relationships remain within one setup or have credible datum transfer.
- Confirm stock/fixture/tool/holder/CAM/post revisions match the part when CAM is included.
- Confirm posted-code simulation, prove-out, and first-piece records when claiming shop approval.
- Confirm gauges/CMM/probe/functional fixtures can access and resolve each CTQ with adequate uncertainty.
- Verify material and special-process certificate requirements.
- Confirm production BOM and router revisions agree with the released design configuration; reconcile manufacturing-only items, substitutions, lot/serial/firmware records, and as-built deviations.
- Confirm cost and material-yield results state their stock, batch, nesting/cut/build, scrap/rework, remnant, and packaging assumptions.
- Confirm robotics performance/safe-state tests and reliability-risk actions are closed or explicitly approved as release-blocking deviations.
- Confirm any release-driving robot multibody/contact/controls result has controlled per-link mass properties, solver/time-step/sensitivity evidence, load reconciliation, limitations, and required independent physical correlation.

## Gate 7 — Assemble immutable release

Create a revision directory containing only controlled deliverables. Run
`scripts/suite_release_validate.py` first and include its passing report. Write
the manifest inside that root. Use `scripts/release_manifest.py create` with
artifact metadata to record path, size, SHA-256, configuration, generator/version,
generation-record hash, and source lineage, then use `verify` before handoff. Verification
rejects unlisted extra files unless `--allow-extra` is deliberately selected for
a non-release diagnostic.

Typical contents:

- FCStd, generator, exact inputs.
- STEP and reimport audit.
- Drawing PDF and TechDraw source.
- Process-specific DXF/3MF/STL/G-code only when required.
- Model audit, BOP check, parameter sweep, DFM, CAM, calculations, inspection plan/results.
- Analysis plan/load cases/allowables/convergence/correlation, robot dynamics/controls contract where applicable, tolerance/metrology/capability evidence, additive build qualification records, production router, cost/yield/waste report, and reliability/risk records.
- Open-issues/deviation record and approvals.
- For assemblies: child/component records, configuration matrix, reconciled eBOM/mBOM/as-built/service views as applicable, joint/DOF and fit records, motion/collision results, fastener register, mass properties, approved sequence, exploded/assembly drawings, and physical build acceptance when available. When instructional media is a deliverable, include source/configuration hashes, prescribed-motion contract, frame manifest/PNGs, encoded media, storyboard/manual, TechDraw source/PDF/SVG, BOM-callout reconciliation, visual QA and stale-derivative check.
- For robotics: controlled coordinate/joint/inertial model, actuator/transmission sizing, motion-load and thermal evidence, verified multibody/controls/load-transfer/correlation package when required, braking/power-loss/hard-stop analysis, accuracy/calibration plan, cable/sensor interfaces, and performance/safety verification records.
- Release manifest.

Do not include stale intermediate exports with ambiguous names.

## Gate 8 — Verdict

Copy `assets/release-checklist.md` and issue:

- `PASS — production candidate`: all technical gates pass; name outstanding authorization/supplier acceptance.
- `CONDITIONAL`: exact waivers/open actions and invalidated claims.
- `FAIL`: blocking defects and corrective owners.
- `RELEASED`: only after authorized signatures/records exist under the organization’s process.

List checks executed, tool versions, input checksums, results, and checks not performed. Never substitute “looks good” for evidence. A CAD assembly verdict must not claim that the built assembly passed inspection or function testing.

## Script invocation

Inspect local `FreeCADCmd --help`; typical usage is:

```text
FreeCADCmd scripts/freecad_model_audit.py --pass \
  --input part.FCStd --target Body --output audit.json

FreeCADCmd scripts/freecad_parameter_sweep.py --pass \
  --input part.FCStd --cases sweep-cases.json --target Body \
  --output sweep-report.json
```

Run the standard-Python manifest script with the system Python.
