# Production part brief

## Control

- Project / part number:
- Part name:
- Revision:
- Owner / approvers:
- Requested maturity: concept / prototype / production candidate / released
- FreeCAD / OpenCASCADE version:
- Units and projection:
- Governing standards and revisions:
- Product level: individual part / subassembly / top assembly
- Configurations / variants / effectivity:

## Function and interfaces

- Primary function:
- Mating parts and interface control documents:
- Assembly / service sequence:
- Expected motion, joints, stops, and degrees of freedom:
- Critical-to-function features:
- Prohibited failure modes:

## Design environment

- Load cases and duty cycle:
- Stiffness / deflection / life targets:
- Temperature / corrosion / chemicals / cleanliness:
- Safety or regulatory classification:
- Required calculations or simulations:
- Analysis verification, convergence, uncertainty, and test-correlation basis:

## Product definition

- Material grade and condition:
- Heat treatment:
- Coating / finish / marking:
- Thread system:
- General tolerance:
- Critical dimensions / GD&T / surface texture:
- Mass or envelope limits:

## Parameter provenance

| Parameter | Value / unit | Allowed range / set | Type | Requirement source / revision | Owner |
|---|---|---|---|---|---|

## Product structure and sourced components

| Definition / occurrence | Make / buy / standard / ECAD / consumable | Part number / standard / revision | Quantity / configuration | Source record | Approval |
|---|---|---|---|---|---|

- Governing BOM and item/find-number convention:
- Required BOM views: eBOM / mBOM / as-planned / as-built / as-maintained
- Procurement, approved-alternate, lot/serial, firmware, and where-used requirements:
- Component licensing / redistribution constraints:
- Rigid and flexible subassemblies:
- ECAD board revision, variant, source hash, and coordinate transform:

## Assembly interfaces

| Interface / joint | Occurrences / datums | Function / expected DOF | Fit / tolerance stack | Motion / clearance test | Inspection |
|---|---|---|---|---|---|

- Fastener preload / torque / locking authority:
- Cable, connector, antenna, airflow, thermal, and service envelopes:
- Required assembly, exploded, installation, and service views:
- Mass / center-of-gravity / inertia targets:

## Robotics and powered mechanisms

- Robot/mechanism type and coordinate-frame convention:
- Motion profile, workspace, singularity, home, and limit requirements:
- Actuator/transmission/brake architecture and sizing authority:
- Accuracy, repeatability, backlash/compliance, and calibration targets:
- Power-loss, gravity, hard-stop, and safe-state requirements:
- Sensor, cable-carrier, connector, grounding, and controller/URDF interfaces:

## Manufacturing

- Intended process and quantity:
- Supplier / machine / controller:
- Stock form and allowance:
- Setups, workholding, and datum transfer:
- Secondary operations:
- Supplier capability references:
- Production router / work centers / special-process qualifications:
- Purchased versus finished material and target utilization:
- Nesting / cut / additive-build constraints and remnant policy:
- Setup, cycle, tooling, inspection, rework, yield, and packaging cost basis:
- Alternative-process and batch-size comparison:

## Reliability and risk

- Risk method and acceptance authority:
- Safety/mission/business-critical functions and hazards:
- Required DFMEA / PFMEA / FMECA / fault-tree interfaces:
- Reliability, design-life, maintenance, and spares targets:
- Residual-risk and action-closure evidence:

## Inspection

- Acceptance authority:
- Datum simulation:
- CTQ characteristic and gauge mapping:
- Sampling / first article:
- Certificates / reports:

## Deliverables

- Native FCStd:
- Regeneration script and data:
- STEP:
- Drawing PDF:
- Process file (DXF / mesh / G-code):
- Audit, DFM, CAM, analysis, production-router, BOM/configuration, material-yield/cost, risk, and inspection records:

## Open issues and assumptions

| ID | Type | Statement | Consequence | Evidence / decision required | Owner | Status |
|---|---|---|---|---|---|---|

## Release gates

- [ ] Engineering contract approved
- [ ] Design-intent matrix complete
- [ ] Parametric model and envelope validated
- [ ] Sourced components have exact identity, provenance, geometry verification, and use-rights disposition
- [ ] Assembly hierarchy, joints/DOF, configurations, fits, motion/clearance, BOM, sequence, and mass properties validated
- [ ] Engineering analysis has traceable load cases, allowables, equilibrium, convergence, uncertainty, and correlation evidence
- [ ] Robotics actuator/transmission/performance/safe-state requirements validated, if applicable
- [ ] eBOM, mBOM/as-planned, as-built, and service views reconciled as applicable
- [ ] DFM dispositions closed
- [ ] Production route, cost, material yield, nesting/cut/build utilization, remnants, and waste dispositions approved
- [ ] Reliability/risk actions closed and residual risk accepted
- [ ] CAM review/prove-out complete, if applicable
- [ ] Drawing and inspection plan checked
- [ ] Native and exchange geometry audited
- [ ] Revision manifest and checksums recorded
- [ ] Human and supplier approvals captured
