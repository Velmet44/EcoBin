---
name: freecad-additive-manufacturing-engineering
description: Engineer production additive-manufactured FreeCAD parts and qualified build routes. Use for FDM/MEX, SLA/DLP, SLS/MJF, binder jetting, metal powder-bed fusion, printed robot parts, orientation, supports, witness coupons, anisotropy, shrink or warp compensation, holes/threads/inserts, internal-channel cleaning, post-processing, NDE, build files, AM qualification, or a claim that a 3D-printed part is production ready.
---

# FreeCAD Additive Manufacturing Engineering

Runtime compatibility: Codex and Claude Code; Python 3.10+ for deterministic contract checks; exact slicer/build-preparation software and machine must be project-pinned.

Engineer the complete process chain, not only an STL. A visually successful print does not establish geometry, material properties, fatigue life, cleanliness, or repeatability.

Use `../freecad-tolerance-metrology-and-process-capability/SKILL.md` for CTQs, fits, compensation evidence, and conformity decisions; `../freecad-engineering-analysis-and-optimization/SKILL.md` for anisotropic/thermal/structural substantiation; `../freecad-manufacturing-planning-and-material-optimization/SKILL.md` for packing, support waste, yield, and cost; and `../freecad-release-validation/SKILL.md` for native/STEP/3MF/STL/build-file release.

Read `references/am-process-and-qualification.md` and `references/am-design-postprocess-and-inspection.md`. Copy `assets/additive-manufacturing-contract.json` and `assets/build-and-coupon-register.csv`. The bundled contract is a non-releasable template and returns `DRAFT`; change `record_state` to `controlled_evidence` only after replacing every fixture value with controlled project evidence. Run `scripts/additive_contract_validate.py`.

## Gate 1 — Select and qualify the exact process tuple

Record supplier/site, machine/configuration, AM process category, material/feedstock lot and condition, parameter-set/build-strategy revision, build preparation and software versions, orientation, position, supports, atmosphere, reuse policy, and all post-processing.

For production evidence, bind the feedstock certificate and reuse history, machine
qualification/calibration/maintenance, build parameter/support/orientation/log
hashes, operator and site qualifications, EHS controls, same-build coupon results,
post-process certificates, serials, inspection, and authority-matched approvals.

General standards and vendor rules are screening inputs. Qualify representative geometry on the exact tuple. Define requalification triggers for maintenance, calibration, material/parameter/site/orientation/scale or post-process changes.

## Gate 2 — Design for the complete state chain

Model and review every state: as-built, depowdered/cleaned, support-removed, stress-relieved, heat-treated/HIP, machined, surface-finished, coated, conditioned, and assembled as applicable.

Check walls, pins, holes, slots, overhangs, trapped material, escape/drain paths, supports and removal access, recoater/load direction, thermal mass transitions, curl/warp, surface stair-stepping, anisotropy, build envelope, nesting, marking, fixturing datums, machining stock, and sacrificial tabs.

For precision bearing/shaft/seal datums, repeated threads, or accurate hole patterns, default to a qualified insert or post-machining route unless direct-print capability is demonstrated. Printed press fits depend on material, orientation, surface, moisture, temperature, creep, and machine.

## Gate 3 — Qualify material and physics

Use allowables for the exact process/material/orientation/post-process/environment, not bulk wrought or injection-molded datasheet values. Define coupon locations/orientations and tests for tensile, fatigue, density/porosity, surface, thermal, creep, impact, flammability, sterilization, or other governing properties.

Account for residual stress, defects, anisotropy, interfaces/layers, notches, surface condition, moisture and temperature. Route release-driving structural conclusions through the analysis skill and correlate to physical tests proportional to consequence.

## Gate 4 — Establish geometric capability and compensation

Use ISO/ASTM 52902-style representative artifacts or equivalent controlled studies across required build positions, orientations, feature sizes, and states. Link every CTQ to the tolerance-capability contract, uncertainty, decision rule, and control plan.

Keep nominal product geometry authoritative. Version and validate manufacturing compensation separately; preserve before/after artifact data and its validity envelope.

## Gate 5 — Plan post-process, cleaning, and inspection

Define support/powder/resin removal, cleaning validation, stress relief/heat treatment/HIP, machining, polishing/blasting, coating, sealing, conditioning, marking, preservation, and inspection sequence.

Internal passages need demonstrated removal/cleaning and inspectability. Define NDE capability and acceptance criteria for consequential internal defects; do not assume CT can detect or size every relevant flaw.

## Gate 6 — Control build and release data

Release the nominal FCStd/STEP, controlled tessellation/build-preparation inputs, orientation/support/build layout, parameter-set and machine configuration, material lot and reuse history, witness coupons, in-process monitoring, post-process/inspection records, deviations, and hashes.

Verdicts:

- `PASS — AM production candidate`: the exact process tuple, CTQs, material basis, coupons, post-process, inspection, change control, and approvals are complete.
- `DRAFT`: concept/prototype without a qualified route.
- `CONDITIONAL`: bounded missing supplier/coupon/inspection evidence is explicit.
- `FAIL`: a functional, material, geometric, cleaning, inspection, or traceability gate is blocked.

The validator cannot certify a build, machine, material, supplier, or physical part.
