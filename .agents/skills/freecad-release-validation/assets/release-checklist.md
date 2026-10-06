# Manufacturing release checklist

## Control

- Part number / name:
- Revision:
- Maturity:
- Native model checksum:
- FreeCAD / OpenCASCADE / add-on versions:
- Governing standards / revisions:
- Design / manufacturing / quality approvers:

## Requirements and analysis

- [ ] Production brief and interface requirements approved
- [ ] Material, condition, process, finish, and quantity controlled
- [ ] Load cases, calculations/simulations, and assumptions reviewed
- [ ] Fits, clearances, and tolerance stacks approved
- [ ] CTQ capability/FAI, metrology uncertainty, decision rules, and supplier scope approved
- [ ] Open issues/deviations dispositioned

## Native CAD

- [ ] Deterministic recompute has no error states
- [ ] Expected targets and solid counts
- [ ] Final shape valid, closed, and positive volume
- [ ] GUI Check Geometry with BOP passed
- [ ] Production sketches fully constrained or exceptions approved
- [ ] Dependency graph and topology-sensitive references reviewed
- [ ] Nominal and parameter-envelope sweep passed
- [ ] Mass properties and envelope independently checked

## DFM and CAM

- [ ] Named process/supplier capability reviewed
- [ ] DFM BLOCKER/MAJOR findings closed
- [ ] Workholding, datum transfer, tool/mold/form/build access credible
- [ ] Secondary-process allowance and distortion addressed
- [ ] Additive process tuple, coupons, state chain, compensation, cleaning and post-process qualified, if applicable
- [ ] CAM model/job/post/tool/setup revisions match, if applicable
- [ ] Posted-code simulation/prove-out/first-piece evidence complete, if claimed

## Product definition and inspection

- [ ] Drawing identity, units, projection, scale, material, finish complete
- [ ] Dimensions/GD&T/threads/surfaces/edges unambiguous
- [ ] All TechDraw attachments visually and numerically rechecked
- [ ] CTQ-to-process-to-inspection matrix complete
- [ ] Measurement access, datum simulation, uncertainty, and sampling accepted

## Exchange artifacts

- [ ] STEP/B-rep reimport passes geometry checks
- [ ] Native/exchange solid count, envelope, volume, and placement agree
- [ ] DXF profiles/flat pattern verified, if applicable
- [ ] Mesh units, tessellation, manifold state, and reimport verified, if applicable
- [ ] PDFs and setup sheets visually checked

## Assembly instructional media

- [ ] Native simulation is identified as prescribed kinematics, not collision/dynamics proof
- [ ] Root/child/configuration/BOM hashes match frame, media, TechDraw and manual derivatives
- [ ] Frame count/order/joint values/critical poses/camera and image hashes verified
- [ ] Exploded moves reset to authoritative design placements
- [ ] Instruction steps, occurrences, find numbers, quantities and BOM callouts reconcile
- [ ] Tools, torque/process, consumables, safety, inspection and rework details complete
- [ ] PNG sequence, encoded media, manual, TechDraw exports and visual QA report controlled

## Release

- [ ] Only current controlled deliverables included
- [ ] Release manifest created and verified
- [ ] Superseded artifacts quarantined
- [ ] Supplier exceptions captured
- [ ] Required human approvals recorded

## Verdict

- Result: PASS — production candidate / CONDITIONAL / FAIL / RELEASED
- Checks not performed:
- Conditions / residual risk:
- Approval references:
