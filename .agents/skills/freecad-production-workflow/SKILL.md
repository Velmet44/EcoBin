---
name: freecad-production-workflow
description: Orchestrate a mechanical part, robot, or assembly from requirements through governed component sourcing, robust FreeCAD modeling, mechanism and assembly engineering, multibody/FEA evidence, tolerance and process capability, additive qualification, traceable assembly instructions, controlled BOM/configuration, DFM, manufacturing optimization, CAM, risk, and release verification. Use for production-intent FreeCAD parts, mechanically credible robotics, CAD/CAM handoff, BOM/exploded/tutorial packages, or controlled manufacturing revisions.
---

# FreeCAD Production Workflow

Runtime compatibility: Codex and Claude Code; Python 3.10+ for bundled validators and FreeCAD 1.1.2/FreeCADCmd for CAD runtime checks.

Treat “production-ready” as a gated engineering claim, not a styling goal. Build the evidence package needed for a qualified designer, manufacturer, and inspector to approve the part. Never imply that a model alone proves strength, process capability, regulatory compliance, or safe machine code.

Target FreeCAD 1.1.2 or newer compatible 1.1.x behavior unless the user pins another version. Record the exact FreeCAD and OpenCASCADE versions used.

## Route work to the companion skills

Use the smallest applicable path:

- Build or revise geometry: use `../freecad-parametric-modeling/SKILL.md`.
- Source/import standard or purchased hardware, servos, boards, or supplier CAD: use `../freecad-component-sourcing/SKILL.md`.
- Structure and verify subassemblies, mechanisms, BOMs, fits, motion, and exploded views: use `../freecad-assembly-engineering/SKILL.md`.
- Size and verify robot mechanisms, actuators, transmissions, brakes, sensors, accuracy, and coordinate models: use `../freecad-robotics-mechanism-engineering/SKILL.md`.
- Build and validate force-driven multibody, contact, actuator, and controls physics for robots: use `../freecad-robot-motion-dynamics-and-validation/SKILL.md`.
- Plan calculations, FEA, verification/validation, DOE, or constrained optimization: use `../freecad-engineering-analysis-and-optimization/SKILL.md`.
- Allocate fits/CTQs and prove process capability, metrology, uncertainty, and conformity decisions: use `../freecad-tolerance-metrology-and-process-capability/SKILL.md`.
- Qualify production additive parts, process tuples, coupons, post-processing, cleaning, inspection, and build data: use `../freecad-additive-manufacturing-engineering/SKILL.md`.
- Create controlled native animation, exploded TechDraw, frame/video media, and assembly/service tutorials: use `../freecad-assembly-visualization-and-work-instructions/SKILL.md`.
- Build and reconcile eBOM, mBOM, as-planned, as-built, and service configurations: use `../freecad-production-bom-and-configuration/SKILL.md`.
- Review process feasibility and cost drivers: use `../freecad-dfm-review/SKILL.md`.
- Create production routers and quantify cost, time, yield, nesting, remnants, and waste: use `../freecad-manufacturing-planning-and-material-optimization/SKILL.md`.
- Perform DFMEA/PFMEA/FMECA, failure propagation, action closure, and residual-risk review: use `../freecad-reliability-and-risk/SKILL.md`.
- Create a FreeCAD CAM plan or inspect posted G-code: use `../freecad-cam-planning/SKILL.md`.
- Audit and release native CAD, exchange files, and drawings: use `../freecad-release-validation/SKILL.md`.

For a manufactured individual part, use parametric modeling, applicable analysis, tolerance/process capability, DFM, manufacturing planning/material optimization, optional CAM, and release validation. Add additive-manufacturing engineering for a production AM route. For a product assembly, govern bought/standard parts first, build every make part separately, perform assembly engineering, reconcile the production BOM, then complete DFM/DFA, manufacturing planning, risk review, and release validation; add the visualization/work-instructions skill when tutorials or exploded media are deliverables. For a powered mechanism or robot, add robotics mechanism engineering and reliability/risk from the first architecture decision, plus robot motion dynamics when inertial, contact, flexible-body, actuator, or control response drives a claim. Copy `assets/production-brief.md` into the project and maintain it as the traceable design record.

## Gate 0 — Classify the requested maturity

Label the result explicitly:

1. **Concept** — geometry communicates an idea; manufacturing and verification are incomplete.
2. **Prototype** — geometry is buildable by a named process under stated assumptions; production controls are incomplete.
3. **Production candidate** — model, DFM, tolerance scheme, drawing, inspection plan, and release artifacts pass internal checks.
4. **Released** — an authorized human has approved the controlled package and the selected supplier has accepted process capability.

Do not silently promote one level to another.

## Gate 1 — Establish the engineering contract

Capture the following before committing irreversible design choices:

- Function, mating interfaces, motion, assembly sequence, service access, and failure consequences.
- Loads, load cases, duty cycle, stiffness/deflection targets, shock, vibration, fatigue, temperature, corrosion, chemicals, cleanliness, and design life.
- Material grade, condition/temper, heat treatment, coating, finish, grain or build-direction constraints, and permitted substitutions.
- Manufacturing process, quantity, supplier capabilities, stock form, machine axes/envelope, tool access, workholding, secondary operations, and inspection equipment.
- Units, projection convention, governing dimensioning/tolerancing system, thread system, general tolerances, critical characteristics, and acceptance authority.
- File deliverables, naming, revision, confidentiality/export constraints, and required native/history data.
- Product structure, configurations/effectivity, make/buy/standard/ECAD classifications, component source/use-rights requirements, and expected BOM/assembly/exploded/service outputs.

Classify every missing input:

- **Blocking** — guessing could change safety, fit, function, material, process, tolerance, or acceptance. Stop that decision and request the value.
- **Assumption allowed** — choose a conservative, reversible value, label it `ASSUMPTION`, give its consequence, and place it in the open-issues register.
- **Supplier-dependent** — present a candidate and require supplier confirmation.

Read `references/evidence-and-approval.md` for the claim and approval policy.

## Gate 2 — Create a design-intent matrix

For each functional feature record:

| Feature | Function / mate | Driving requirement | Datum relation | Tolerance / finish | Process | Inspection |
|---|---|---|---|---|---|---|
| Stable ID | What it does | Requirement source | Functional frame | Only what function needs | Proposed operation | Feasible method |

Use stable feature names such as `mount_face_A`, `bearing_bore_01`, and `datum_hole_B1`. Do not use generated edge names as the design vocabulary.

Perform fits, clearance, tolerance-stack, fastener, thermal, and load calculations outside the feature tree when required. Store inputs, units, equations, sources, safety factors, and results. A CAD constraint is not a substitute for an engineering calculation.

For assemblies, create separate matrices for definition/occurrence structure, joints/expected DOF, functional interfaces/fits, fastener joints, and assembly/service sequence. A solved nominal assembly is not evidence that these matrices pass.

Invoke engineering-analysis-and-optimization for any release claim that depends on strength, stiffness, buckling, fatigue, vibration, temperature, contact, impact, or an optimized design. Require allowable provenance, load-case traceability, equilibrium checks, convergence evidence, uncertainty, and test correlation appropriate to consequence. A solver contour or topology-optimization shape is not release evidence by itself.

Invoke tolerance-metrology-and-process-capability for every production CTQ or fit. Require an exact supplier/site/machine/process/material/setup-orientation/state scope, representative evidence or justified FAI/100% inspection, measurement uncertainty, decision rule, guard band, and change triggers. A machine brochure or generic printing rule is not part capability.

## Gate 3 — Build robust parametric geometry

Invoke the parametric-modeling skill. Require:

- A manufacturing- and inspection-oriented origin/datum scheme.
- Named parameters with explicit units and provenance.
- Fully constrained production sketches unless a documented controlled degree of freedom is intentional.
- Stable references to origin planes, datums, master sketches, and binders instead of opportunistic generated faces/edges.
- Feature ordering that preserves design intent and defers cosmetic fillets/chamfers.
- A parameter envelope with nominal plus relevant limit cases.
- A valid final solid and an auditable model tree.

When standard or purchased components are required, invoke the component-sourcing skill and block production-candidate status until exact identities, controlling evidence, hashes, and license/redistribution decisions are resolved. Keep imported components as separate controlled definitions with stable assembly datums.

## Gate 3A — Engineer assemblies when present

Invoke the assembly-engineering skill for every subassembly, top assembly, or mechanism. Require:

- Individual definition → subassembly → top-assembly hierarchy with exact child revisions and configuration effectivity.
- Stable occurrence IDs, datums/LCS, intentional grounding, joint/DOF ledger, cold-solve tests, and rigid/flexible subassembly decisions.
- Worst-case fit/tolerance analysis, collision and minimum-clearance tests across motion, fastener-joint records, installation/service/tool access, and ECAD/cable envelopes.
- Recursive BOM reconciliation including non-geometric consumables; mass/CoG/inertia evidence; assembly and exploded drawings with balloon-to-BOM reconciliation.

Solver success, an exploded view, native generated BOM, and nominal clash-free geometry are each necessary/usable evidence but never a complete assembly approval.

## Gate 3B — Engineer robotics and powered mechanisms when present

Invoke robotics-mechanism-engineering for powered axes, linkages, transmissions, end effectors, mobile mechanisms, or robot cells. Require:

- Declared frames, joint conventions, workspace, singularities, home/limit states, accuracy/repeatability targets, and calibration strategy.
- Motion-profile load cases with peak/RMS torque, reflected inertia, duty/thermal margin, transmission efficiency/backlash/compliance, bearing/shaft life, braking, gravity, power-loss, and hard-stop energy.
- Governed motor/drive/gearbox/sensor/cable interfaces and a controller-neutral coordinate/inertial model where software integration is required.
- Physical verification plans for performance and safety functions; CAD kinematics and URDF exports do not certify a robot.

When dynamic response drives sizing, accuracy, contact, stopping, resonance, or safety evidence, invoke robot-motion-dynamics-and-validation. Require numeric per-link mass/CoG/inertia, joint/friction/compliance/contact and actuator/control models, pinned solver/integrator/time step, constraint/energy and sensitivity checks, load transfer, and independent physical correlation. FreeCAD Assembly animation remains visualization only.

## Gate 4 — Review manufacturability

Invoke the DFM skill against the named process and actual supplier/machine capability. Resolve or formally disposition:

- Tool or mold access, internal radii, deep/slender features, thin walls, small holes, undercuts, draft, bend rules, build orientation, supports, powder/resin removal, and post-processing.
- Stock, setups, datum transfer, clamping, distortion, residual stress, deburring, cleaning, heat treatment, coating allowance, and marking.
- Assembly sequence, part count/orientation, fastening/tool access, poka-yoke, adjustment, service/removal paths, cable handling, and inspectability where assemblies are in scope.
- Tolerances and surface requirements that exceed process need or capability.
- Features that are impossible or expensive to inspect.

For additive manufacture, invoke the additive skill before accepting orientation, supports, direct-printed precision interfaces, compensation, allowables, internal cleaning, post-processing, inspection, or build-release data. Never substitute a universal printer clearance for measured process-specific capability.

Record every supplier heuristic with its source and scope. Never turn one vendor’s published capability into a universal rule.

Invoke manufacturing-planning-and-material-optimization after the credible process route is known. Quantify purchased versus finished material, expected yield and rework, stock-size selection, nesting/cut/build utilization, remnant policy, setup and cycle time, tooling/inspection/secondary-operation cost, batch assumptions, packaging, and alternative-process break-even. Preserve functional, safety, quality, grain/build-direction, and supplier constraints when optimizing cost or waste.

## Gate 5 — Plan CAM when requested

Invoke the CAM skill only after geometry and process review. A FreeCAD toolpath preview is not machine approval.

Require an identified machine, controller, postprocessor, stock, work coordinate system, fixture/clamp model, holder/tool assembly, operation sequence, feeds/speeds source, and verification record. Keep posted code quarantined until an authorized machinist completes controller-specific review, backplot/simulation, dry run or single-block prove-out, and first-piece inspection.

## Gate 5A — Reconcile product configuration and risk

Invoke production-bom-and-configuration before release of an assembly or product. Reconcile definition and occurrence structure through eBOM, mBOM/as-planned, as-built, and service views as applicable. Require controlled alternates, effectivity, where-used, manufacturing-only and non-geometric items, procurement identity, lot/serial/firmware traceability, and approved change disposition.

Invoke reliability-and-risk when failures can affect safety, mission, compliance, costly equipment, production continuity, or design life. Link functions and hazards to failure modes, causes, local/next/end effects, prevention/detection controls, verification evidence, actions, and residual-risk approval. Treat the risk record as configuration-controlled and invalidate affected conclusions after design, process, supplier, software, or use changes.

## Gate 6 — Validate and assemble the release

Invoke the release-validation skill. The release package should contain, as applicable:

- Native `.FCStd` file with editable history.
- Controlled child definitions/component records, configuration matrix, reconciled released BOM views, joint/fit/fastener/motion/mass evidence, process-capability and metrology records, and assembly/service instructions with traceable rendered media where applicable.
- Regeneration script and input data when scripted.
- Neutral B-rep exchange file, normally STEP, reimported and compared.
- Controlled PDF drawing and source TechDraw page.
- Process-specific file only where needed: DXF flat/pattern, STL/3MF mesh, or reviewed G-code.
- Material/process/finish specification, additive build/qualification records where applicable, inspection and conformity plan, calculation/CAE/MBD credibility records, DFM and production-router records, cost/yield/waste report, reliability/risk register, automated audit reports, open-issues register, and revision manifest with checksums.

Use one source of truth for each requirement. Do not independently hard-code the same nominal in a spreadsheet, sketch, drawing note, and CAM setup.

## Final verdict

End every full workflow with one verdict:

- `PASS — production candidate`: automated and manual gates pass; identify remaining human/supplier approval.
- `CONDITIONAL`: list exact assumptions, waivers, and actions required.
- `FAIL`: list blocking defects and the owner of each corrective action.

Report evidence, not confidence language. State what was checked, by which tool/version, against which inputs, and what could not be checked. Keep `CAD assembly production candidate` distinct from `physical assembly accepted`.

## Research basis

Read `references/research-basis.md` when updating this suite, resolving a version-sensitive question, or citing the rationale behind the workflow. Verify current software, supplier, and standards status before using it for a new controlled release.
