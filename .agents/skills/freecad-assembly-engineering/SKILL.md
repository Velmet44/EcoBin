---
name: freecad-assembly-engineering
description: Design, structure, test, document, and release FreeCAD mechanical assemblies and mechanisms. Use for part-to-subassembly-to-top-assembly architecture, native FreeCAD Assembly, App::Link components, rigid/flexible subassemblies, joints and DOF, BOM/configurations, fastener joints, tolerance stacks, collision/swept-motion checks, ECAD–MCAD integration, sequence feasibility, mass properties, or assembly release validation. Route rendered animations, exploded tutorials, and work-instruction media to the companion visualization skill.
---

# FreeCAD Assembly Engineering

Runtime compatibility: Codex and Claude Code; Python 3.10+ for contract checks and FreeCAD 1.1.2 for native Assembly, motion, and geometry verification.

Build an assembly as a controlled product structure, not a pile of positioned solids. A solver success proves only that a nominal constraint system solved. It does not prove physical fit, strength, preload, tolerance closure, collision-free motion, installability, serviceability, or an accurate procurement BOM.

Target FreeCAD 1.1.2 or the project-pinned version. Use one assembly architecture per product; do not mix native Assembly, A2plus, Assembly3, and Assembly4 constraints in a release structure.

Read:

- `references/freecad-assembly-workbench.md` for native 1.1.x architecture and capabilities.
- `references/assembly-verification.md` for joints, fits, motion, mass, and test evidence.
- `references/bom-exploded-and-release.md` for product structure, BOM, sequence, drawings, and release.

Use `../freecad-component-sourcing/SKILL.md` before admitting downloaded, standardized, servo, actuator, PCB, or supplier components. Invoke `../freecad-robotics-mechanism-engineering/SKILL.md` for powered axes or robot mechanisms, `../freecad-robot-motion-dynamics-and-validation/SKILL.md` when force-driven dynamics or controls response matters, `../freecad-tolerance-metrology-and-process-capability/SKILL.md` for production fits/CTQs, `../freecad-production-bom-and-configuration/SKILL.md` for manufacturing/as-built/service BOM control, and `../freecad-assembly-visualization-and-work-instructions/SKILL.md` for animation, exploded TechDraw, or tutorial deliverables. Copy `assets/assembly-contract.json`, `assets/interface-fit-register.csv`, and `assets/assembly-sequence.md` into the project.

## Gate 1 — Freeze the assembly contract

Record:

- Top product number/name/revision, owner, maturity, units, coordinate system, configurations/effectivity, and governing ISO or ASME product-definition system.
- Named acceptance-authority role and one intentional grounding declaration per released configuration.
- Intended function, load paths, moving members, installation environment, assembly/disassembly/service needs, safety consequences, and acceptance authority.
- Required interfaces, fits, motion ranges/stops, clearances, mass/CoG/inertia, cable/harness behavior, thermal/coating effects, and test conditions.
- The exact child revision or approved alternate used by each configuration.

Run `scripts/assembly_contract_validate.py`. Run `scripts/interface_register_validate.py` against the CSV and contract to reconcile configuration, occurrence, and test IDs. These check record consistency, not CAD truth or physical acceptance.

## Gate 2 — Build the product hierarchy

Use this recursive structure:

1. **Individual definition** — one controlled manufactured part, standard part, purchased component, PCB assembly, cable, bulk/consumable item, or reference envelope.
2. **Subassembly** — a separately buildable/testable functional group, declared rigid or flexible at its parent.
3. **Top assembly** — configuration-specific product structure and highest-level interfaces.

Rules:

- Keep each released manufactured/purchased definition independently auditable. Never fuse occurrences into a monolithic release Body.
- Use stable part number plus revision/configuration for identity. Give every placement a unique occurrence ID. Item/find number is not the part number.
- Use native Insert Component/App::Link for reusable FCStd definitions. Quarantine, validate, and wrap STEP before linking it.
- Use stable datums/LCS and named interface geometry. Do not mate long-lived joints to transient `Face12`/`Edge37` references.
- Make a subassembly rigid by default at the parent. Make it flexible only when its internal degrees of freedom must participate in the parent mechanism, then test both hierarchy levels.
- Do not create assembly-context cuts in purchased or shared master definitions. Create a controlled derived part/revision if machining or adaptation is real.

## Gate 3 — Plan and test constraints

Create a joint/DOF ledger for every rigid or flexible assembly:

| Joint ID | Occurrence A / datum | Occurrence B / datum | Type | Intended constraint | Limits/home | Expected remaining DOF | Test |
|---|---|---|---|---|---|---|---|

- Ground the intended base/reference; check that accidental additional grounding does not hide overconstraint.
- Record the grounded occurrence, datum, intent, and configuration in the contract. A production-candidate contract with zero or multiple declared grounds for one configuration fails.
- Use the least redundant joint set that expresses design intent.
- Verify every joint resolves to the correct occurrence and stable datum.
- State expected remaining translational/rotational DOF per configuration and compare behavior, not only solver status.
- Record joint limits, home state, mechanical stops, and forbidden overtravel.
- Cold-open/recompute/solve from controlled placements. Do not accept a mechanism that needs undocumented dragging into a solvable pose.
- Test nominal, endpoints, transitions/singularities, and each released configuration.

A CAD joint is kinematic. It does not establish contact pressure, friction, fastener preload, bearing life, structural load path, or safety.

## Gate 4 — Engineer interfaces, fits, and fastener joints

For each close or functional pair, complete the interface/fit register:

- Datum pair and function.
- Classification: forbidden interference, intentional contact, clearance fit, transition/interference fit, or flexible-envelope interaction.
- Fit class or explicit size/geometry limits and the invoked standard/edition.
- Worst-case minimum/maximum clearance or interference, including GD&T, coatings, thermal growth, load/centrifugal deflection, wear, and supplier tolerances.
- Statistical method only when distributions, correlation, capability, and acceptance criteria are justified.
- Lubrication/sealing, inspection method, and physical test evidence.
- Executed test status and evidence artifact; a planned or empty test record does not satisfy a production-candidate gate.

Never mix ISO GPS and ASME Y14.5 defaults silently. Nominal collision-free CAD is not tolerance-safe.

For threaded joints record exact fastener identity, grip, thread engagement, holes/counterbores/countersinks, washer/nut/insert, joint materials, load cases, preload range, torque basis and lubrication/coating state, locking, tool access, inspection/witnessing, and reuse policy. Never infer approved torque from nominal diameter or catalog geometry alone.

## Gate 5 — Verify interference and motion

For every released configuration and relevant mechanism pose:

1. Solve/recompute and record the state.
2. Check exact solid intersections for all non-allowlisted pairs.
3. Check required minimum distances for clearance pairs.
4. Evaluate endpoints, critical events, and the swept path of moving parts, horns/linkages, cables/harnesses, tools, fasteners, and service items.
5. Apply tolerance, thermal, coating, load, and wear margins to the acceptance threshold.
6. Verify stops prevent harmful overtravel and that insertion/removal paths do not require unintended disassembly.

Declare sample step size and adaptive-refinement rule. Discrete frames can miss a collision; use analytical or adaptively refined sweeps for critical pairs. Intentional contact must be pair-specific and documented, never globally ignored.

FreeCAD’s native Create Simulation is prescribed pose generation/animation, not dynamics or collision certification. Use the robot dynamics skill and physical tests where loads, contact, impact, actuator/control response, or safety require them. Use the visualization skill for deterministic frame capture and tutorial media.

## Gate 6 — Verify assembly and service sequence

An exploded view communicates; it does not prove assembly feasibility.

Create ordered assembly and disassembly/service steps with:

- Predecessor dependencies and part/occurrence IDs.
- Insertion/removal path and orientation.
- Tool, wrench/socket/screwdriver sweep, fixture, access, and human-factor envelope.
- Torque/preload/locking, adhesive/lubricant, cure, cleanliness, ESD, and safety notes.
- Inspection checkpoints and rework limits.
- Replaceable items, connector/cable handling, and prohibited force paths.

Verify each path against the actual non-exploded product geometry. Preserve design placements; store exploded transforms as a separate view state. When producing released manuals, route the approved occurrence/BOM/sequence records to the visualization skill and require source hashes, frame/media manifests, TechDraw callout reconciliation, and visual QA.

## Gate 7 — Reconcile BOM, properties, and configurations

The native FreeCAD BOM is useful but is not the sole release authority. Reconcile the recursive occurrence graph against the controlled BOM by part number, revision/configuration, and quantity.

Include make/buy/standard/bulk/consumable/reference classification; description; material/spec/finish for make parts; approved manufacturer/supplier part number for controlled buys; alternate/effectivity; unit of measure; reference designator; mass source; and traceability notes.

Standard, buy, ECAD, bulk, and consumable definitions require a governed component/specification record. For mass, use a positive controlled value for mass-bearing items. Reference/software items may declare `non_mass_item`; a bulk/consumable may be `included_in_parent` or `excluded_with_justification` only with a documented basis.

Geometry-derived BOMs omit adhesives, lubricants, wire, labels, packaging, and installation consumables. Add them deliberately. Reject duplicate occurrence IDs, missing child revisions, quantity mismatches, cycles, stale links, unresolved sources, and absent configuration effectivity.

The assembly contract remains the CAD occurrence authority, not a complete production-planning or procurement database. Hand its reconciled definition/occurrence graph to the production-bom-and-configuration skill for eBOM-to-mBOM transformation, manufacturing-only items, substitutions, lots/serials, firmware, as-built records, where-used, and service effectivity.

## Gate 8 — Verify mass and documentation

For each released configuration and key pose:

- Reject missing, zero, or placeholder density/mass.
- Distinguish CAD-calculated, supplier-provided, measured, and approved override values.
- Multiply occurrences and report total mass, center of gravity, and inertia tensor in a declared coordinate system with uncertainty/margin.
- Require physical measurement where the mass-property requirement is critical.

Create:

- Non-exploded assembly drawing/views for interfaces and acceptance.
- Exploded view(s), connector lines, balloons/find numbers, and parts list.
- Installation/service views where sequence or access is not obvious.

Render PDF/SVG and visually review it. Reconcile every balloon to the released BOM; do not assume automatic synchronization.

## Gate 9 — Release and physical acceptance

Release the top FCStd, exact linked child revisions/hashes, configuration matrix, controlled BOM, component records, joint/DOF ledger, interface/tolerance analyses, collision/motion report, fastener register, mass report, assembly/service instructions, exploded and assembly drawings, STEP reimport evidence, deviations, and approvals.

Every production-candidate test and release-evidence record must name its configuration scope, status, artifact/evidence, and source hash where applicable. Approvals must name the human, role, date, scope, configurations, and decision; a non-empty note is not approval.

Verdicts:

- `PASS — assembly production candidate`: all declared CAD/engineering gates pass; identify remaining supplier/build authorization.
- `CONDITIONAL`: exact configuration, assumptions, waivers, and invalidated claims.
- `FAIL`: blocking structure, source, solve, fit, collision, access, BOM, or evidence defects.
- `RELEASED`: only after authorized configuration approval.

Record built-assembly acceptance separately: measured fits/clearances, torque/locking witness, motion/function/end-stop tests, mass, electrical/ECAD checks, inspection, and nonconformances. No script or nominal CAD review can claim the physical assembly passed.
