---
name: freecad-component-sourcing
description: Source, import, verify, simplify, and govern standard or purchased components for production FreeCAD work. Use for M2/M3 screws, nuts, washers, bearings, inserts, pins, servos, motors, actuators, connectors, Raspberry Pi or Arduino-class boards, KiCad PCB assemblies, supplier STEP files, FreeCAD Fasteners Workbench, public CAD libraries, component provenance, licensing, or deciding whether downloaded geometry is trustworthy enough for release.
---

# FreeCAD Component Sourcing

Runtime compatibility: Codex and Claude Code; Python 3.10+ for record validation and FreeCAD 1.1.2 for geometry import and verification.

For motors, servos, drives, gearboxes, brakes, bearings, encoders, and robot-specific interfaces, use this skill to govern exact purchased identity and geometry, then invoke `../freecad-robotics-mechanism-engineering/SKILL.md` for sizing and system performance. A correctly sourced component is not proof that it is suitable for the mechanism.

Treat imported geometry as evidence of shape, not automatic authority for dimensions, tolerance, material, strength, lifecycle, or redistribution. A component becomes release-eligible only when its exact identity, controlling source, geometry checks, interfaces, and permitted use are recorded.

Target FreeCAD 1.1.2 or the project-pinned version. Record FreeCAD, OpenCASCADE, importer, workbench/add-on version or commit, and import options.

## Choose the controlling source

Use this order unless the project has a stricter approved-source list:

1. Exact manufacturer part-number CAD plus the current controlled product drawing or datasheet.
2. A standards-driven generator using the exact current invoked standard and organization-controlled dimensional data.
3. Supplier CAD cross-checked against the manufacturer drawing.
4. ECAD-authoritative export for a project PCB, with the board revision, variant, and source hash.
5. Curated or community geometry only as an envelope/reference until independently verified.

Do not use a visually similar part, scale one product to impersonate another, or call a generic “9 g servo,” “standard servo,” or “Arduino-like board” release-authoritative.

Read:

- `references/standard-fasteners.md` for hardware identity, holes, threads, and Fasteners Workbench.
- `references/vendor-and-open-components.md` for vendor/community sources and licensing.
- `references/ecad-servos-and-electronics.md` for PCB, controller, connector, servo, and actuator models.

## Gate 1 — Define the immutable identity

Create one record from `assets/component-record.json` per unique definition. Separate a definition from its assembly occurrences.

For a standardized component record:

- Standard identifier and edition, nominal size, pitch, thread tolerance, length, head style, drive, material/property class, finish, and applicable options.
- Do not conflate drive and head. “Allen” means a hexagon-socket drive; “flat” usually means a countersunk head. A hex-socket countersunk screw combines both.

For a manufacturer-specific component record:

- Manufacturer, exact orderable part number, hardware/board revision or configuration, controlling drawing/datasheet number and revision, lifecycle status, and approved alternates.

For ECAD-derived geometry also record project/board ID, revision, fitted variant, source commit/hash, DNP policy, export tool/version, and coordinate transform.

## Gate 2 — Capture provenance and use rights

Preserve the untouched downloaded/generated source. Record:

- Source URL or controlled repository path, publisher, access date, source revision/configuration, and SHA-256.
- License/terms URL, attribution obligations, redistribution decision (`permitted`, `conditional`, `prohibited`, or `unresolved`), and the scope/approver/date of any conditional exception.
- Whether the source is manufacturer, standard generator, supplier, ECAD, curated community, or uncontrolled community.
- Geometry authority: `reference`, `envelope`, `interface-verified`, or `release-candidate`.

Supplier and community models often omit tolerances, finishes, internal details, or revision control. Their website terms may prohibit redistribution even when downloading is allowed. Do not place restricted files in a public repository or release package.

## Gate 3 — Import and normalize without losing evidence

1. Copy the untouched source into controlled incoming storage; never overwrite it.
2. Import into a clean FreeCAD document with recorded options and verify units/scale.
3. Check expected solids, shells/compounds, validity/BOP result, placement, handedness, and bounding box.
4. Compare every critical interface to the controlling drawing: mounting pattern, mating plane, axes, bores, connector position, maximum envelope, and required keepouts.
5. Create a local wrapper with stable named datums/LCS, component metadata, interface geometry, keepouts, and light/detailed representation links.
6. Keep the purchased/standard component as its own definition. Do not fuse it into a manufactured Body or make assembly-only cuts in its source model.
7. Reimport the normalized STEP when exchange is required and compare selected measurements.

Use `scripts/component_record_validate.py RECORD.json --source-file COMPONENT.step`
to reject incomplete or overclaimed records and recompute the controlled geometry
hash. A release candidate also requires measured critical interfaces, mass/CG/inertia
provenance, structured evidence, configuration binding, and acceptance-authority
approval. Script success does not prove the publisher's claims or external standard
content are true.

## Gate 4 — Apply class-specific checks

### Standard fasteners

- Select by standard, function, load, material compatibility, environment, installation, and supply—not diameter alone.
- Define holes from the governing hole/thread/tolerance requirement, never by subtracting a downloaded screw.
- Verify clearance/tapped hole, counterbore/countersink, grip, engagement, washers/nut/insert, tool access, coating, locking, preload/torque basis, and reuse policy in the assembly record.
- Prefer simplified threads for normal assemblies. Model helices only when thread interference, printed/manufactured thread geometry, or a presentation requirement justifies the performance cost.
- Pin the Fasteners Workbench version/commit and verify key dimensions. Its geometry does not define strength, preload, torque, coating, or acceptance.

### Servos, motors, and actuators

Require the exact part and configuration. Capture body/mounting interfaces, output-axis datum, spline or shaft, horn/coupler, hard stops and travel, swept motion, cable exit/bend envelope, connector, service/tool access, mass, center of gravity, and inertia when available.

### PCBs and electrical boards

Prefer the project ECAD export or exact manufacturer model. Retain board outline/thickness, holes/slots, connector mating axes, tall/hot/heavy/metal parts, antenna and voltage keepouts, heat sinks/airflow, cable insertion/bend envelopes, controls, programming/debug access, and both-side component height envelopes. Suppress small passives in a lightweight assembly representation only when their omission cannot hide a required clearance.

STEP is MCAD geometry, not the source of PCB copper, net, fabrication, or assembly authority. The DNP policy and an explicit absent-model list (empty only after checking) are mandatory; missing expected 3D models must be listed and assessed, not silently ignored.

## Gate 5 — Approve or quarantine

Verdicts:

- `APPROVED — release candidate component`: identity and source are exact, critical interfaces are verified, use rights are resolved, and required evidence is linked.
- `CONDITIONAL`: usable for a named scope with explicit missing evidence or limits.
- `REFERENCE ONLY`: placement/envelope aid; not authoritative for release decisions.
- `REJECTED`: wrong/ambiguous identity, scale/geometry failure, unresolved critical mismatch, prohibited use, or missing controlling evidence.

An upstream model, drawing, standard edition, board revision, or supplier change is an engineering change. Re-hash, compare, and revalidate before replacing the controlled component.

## Deliverables

Return the controlled source, normalized FCStd/STEP as allowed, wrapper with datums and envelopes, completed component record, dimensional verification evidence, license/terms disposition, representation notes, and verdict. Route occurrence, BOM, fit, motion, and installation work to `../freecad-assembly-engineering/SKILL.md`.
