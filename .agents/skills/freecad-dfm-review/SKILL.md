---
name: freecad-dfm-review
description: Review FreeCAD or neutral mechanical part and assembly definitions for design-for-manufacturing, design-for-assembly/service, and inspection, then propose traceable corrections. Use for CNC milling or turning, sheet metal, additive, molding, casting/forging, supplier review, tolerance/finish rationalization, tooling/access/workholding, fastener and assembly access, part-count/orientation reduction, serviceability, feature feasibility, process selection, cost-risk reduction, or pre-release DFM/DFA signoff.
---

# FreeCAD DFM Review

Runtime compatibility: Codex and Claude Code; FreeCAD 1.1.2 is recommended for native-model inspection, while neutral-file reviews can be performed without it.

Review the part against a named manufacturing route, quantity, material, supplier/machine capability, and inspection plan. Never describe geometry as universally manufacturable.

## Establish the review basis

Require or explicitly mark unknown:

- Part revision and authoritative file.
- Function, critical interfaces, datum scheme, failure consequences, and maturity.
- Material grade/condition, stock form, heat treatment, finish/coating, and permitted substitutions.
- Intended primary and secondary processes, quantity, supplier, machines, axis count, tooling, and inspection equipment.
- Dimensional/GD&T system and exact standard revision.
- General and critical tolerances, surface texture, cosmetic zones, and edge requirements.
- Assembly hierarchy/configuration, mating parts, joint/interface register, fastening method, assembly/service sequence, and supplier/component records when an assembly is reviewed.

If the process is undecided, compare candidate processes and recommend a route; do not apply every process’s rules to one model.

This skill establishes feasibility and cost-risk findings. Invoke `../freecad-manufacturing-planning-and-material-optimization/SKILL.md` when the work requires a controlled production router, quantitative material utilization, nesting/cut/build optimization, cycle time, yield/rework, cost roll-up, remnant handling, packaging, or process break-even analysis.

Invoke `../freecad-tolerance-metrology-and-process-capability/SKILL.md` when a release claim depends on a fit, CTQ, Cp/Cpk/Pp/Ppk, supplier capability, measurement uncertainty, guard band, compensation map, or FAI/control plan. Invoke `../freecad-additive-manufacturing-engineering/SKILL.md` for any production additive route; the short additive checklist here is only a DFM screening layer.

Read:

- `references/cnc-machining.md` for milling and turning.
- `references/other-processes.md` for sheet metal, additive, molding, casting, and forging.
- `references/product-definition.md` for tolerancing, finish, drawing, and inspection.

## Inspect by functional feature

Create a row for each functional or high-risk feature:

| ID | Feature / function | Process operation | Access / setup | Capability concern | Inspection | Severity | Recommendation |
|---|---|---|---|---|---|---|---|

Use stable intent names, not FreeCAD edge numbers.

Trace:

1. Raw stock or preform.
2. Setup and datum establishment.
3. Roughing/forming/build operations.
4. Stress relief/heat treatment where applicable.
5. Finishing and critical feature creation.
6. Deburr, clean, coat, mark, and assemble.
7. Inspection and packaging.

Flag any feature that has no credible operation or no access for its tool, mold action, forming tool, support removal, cleaning, or gauge.

For an assembly, also trace receiving/kitting, orientation and error-proofing, joining/fastening, adjustment, cable/connector handling, inspection/function test, sealing/lubrication/adhesive cure, service/disassembly, and packaging.

## Review dimensions and material together

Check:

- Tool/mold/form access from actual directions.
- Internal radii and bottom geometry against available cutters/tool nose/electrode/mold tooling.
- Hole diameter-to-depth, thread reach/runout, pocket width-to-depth, wall/rib/slenderness, and minimum ligament.
- Undercuts, re-entrant geometry, trapped volume/powder/resin, closed cavities, and inaccessible deburr.
- Stock allowance, near-net process variation, heat-treat/coating growth, shrink/springback, and distortion from residual stress or clamping.
- Workholding surfaces, clamp loads, jaw/tool/holder clearance, part rigidity, and how the part remains attached during cut-off.
- Setup count, datum transfer, same-setup relationships, tool changes, standard tool sizes, and opportunities for symmetry/pattern reuse.
- Burr direction, edge break, corner safety, cleaning, drainage, chip evacuation, coolant access, and marking.
- Grain/fiber/build direction and anisotropy where applicable.
- Part count, symmetry/orientation ambiguity, insertion paths, reach/visibility, driver/wrench/socket swing, tightening sequence, captive hardware, blind operations, connector keying, cable bend/strain relief, service replacement, and risks of damaging adjacent parts.
- Fit class and worst-case tolerance closure, coating/thermal effects, fastener grip/engagement/preload method, and whether joint access remains possible in the actual sequence.

Treat published vendor limits as screening thresholds only. Geometry, material, machine, tooling, orientation, and quality level interact.

## Rationalize tolerances and finish

For every tight tolerance or finish:

1. State the functional failure it prevents.
2. Identify the controlled feature and datum relationship.
3. Confirm the selected process can hold it after all secondary operations.
4. Confirm it can be measured with adequate uncertainty and access.
5. Include the requirement in the tolerance stack.
6. Relax or localize it when function does not justify cost.

Do not infer production capability from nominal machine accuracy, a vendor design guide, or a single successful build. Route quantified capability and conformity decisions to the tolerance skill.

Do not infer tolerance from decimal places unless the governing drawing practice explicitly makes that rule. Do not put a blanket tight tolerance on the entire part.

Select datum features from function and repeatable physical contact, then verify they can be manufactured and simulated in inspection. Avoid contradictory size, position, profile, and surface requirements.

## Evaluate process risk and cost

Classify each finding:

- `BLOCKER` — no credible route, unsafe/uninspectable, violates a controlling requirement, or relies on an unavailable capability.
- `MAJOR` — likely scrap, distortion, unstable setup, special tooling/process, or significant quality/cost risk.
- `MINOR` — avoidable setup/tool/time burden or documentation ambiguity.
- `OPPORTUNITY` — simplification or cost reduction without requirement impact.
- `CONFIRM` — feasible only after supplier/process confirmation.

Do not assign pass/fail solely from a generic ratio. Combine geometry evidence with supplier data and engineering judgment.

Map findings to the verdict:

- Any unresolved `BLOCKER` produces `FAIL`.
- Any unresolved `MAJOR` or release-critical `CONFIRM` produces `CONDITIONAL` at best.
- `PASS` requires all `BLOCKER`/`MAJOR` findings closed and all capability assumptions needed for release confirmed.
- `MINOR` and `OPPORTUNITY` findings may remain only with an owner/disposition and no requirement impact.

## Propose parametric corrections

For every model change:

- Preserve the requirement or state the tradeoff.
- Name the parameter/feature to change and the target relationship, not only a guessed value.
- Prefer standard tools, stock, gauges, threads, bend radii, and finish processes available to the selected supplier.
- Preserve stable datums and interfaces.
- Do not solve an assembly problem by silently modifying a supplier part, creating assembly-only cuts in a shared master, or relying on forced/flexible installation without analysis.
- Update related tolerance stacks, drawings, CAM, calculations, and inspection.
- Re-run the model parameter envelope after editing.

Example: recommend `inside_corner_radius >= selected_cutter_radius + process_clearance` and ask the machinist to approve the cutter, instead of hard-coding a universal 3 mm radius.

## Output

Copy `assets/dfm-report.md` and complete:

- Review basis and exclusions.
- Process route and setup concept.
- Feature findings with evidence and severity.
- Tolerance/finish/inspection review.
- Proposed parametric changes and functional impacts.
- Supplier questions.
- Assembly/service sequence, tool/access, fastening, error-proofing, configuration, and physical build-test findings when applicable.
- Residual risks, assumptions, and verdict: `PASS`, `CONDITIONAL`, or `FAIL`.

A DFM `PASS` means no unresolved issue was found against the stated basis; it is not a manufacturing guarantee or release authorization.
