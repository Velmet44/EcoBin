---
name: freecad-assembly-visualization-and-work-instructions
description: Create traceable FreeCAD assembly animations, exploded views, TechDraw pages, frame sequences, videos/GIFs, and assembly or service tutorials. Use for motion demonstrations, Create Simulation, exploded diagrams, balloons, step images, manuals, work instructions, deterministic camera capture, visual BOMs, or publishing assembly instructions while keeping kinematics, collision, dynamics, BOM authority, and physical acceptance separate.
---

# FreeCAD Assembly Visualization and Work Instructions

Runtime compatibility: Codex and Claude Code; FreeCAD GUI 1.1.2 or a project-pinned version for native simulation/frame capture; Python 3.10+ for package validation; an independently pinned encoder for video/GIF output.

Produce reproducible instructional derivatives from a controlled assembly. FreeCAD native animation is prescribed kinematics, not collision or dynamics evidence. An exploded view communicates order and identity; it does not prove insertion, tool access, or physical assembly.

Use `../freecad-assembly-engineering/SKILL.md` for authoritative occurrences, joints/DOF, fits, collision and sequence feasibility; `../freecad-production-bom-and-configuration/SKILL.md` for find numbers and quantities; and `../freecad-robot-motion-dynamics-and-validation/SKILL.md` for force-driven physics.

Read:

- `references/freecad-native-animation-and-capture.md`
- `references/exploded-techdraw-and-instructions.md`
- `references/visual-qa-and-release.md`

Copy `assets/visualization-instruction-contract.json`, `assets/frame-manifest.csv`, `assets/instruction-storyboard.csv`, and `assets/visual-qa-checklist.md`. The bundled JSON is a template and returns `DRAFT`. For a production candidate, run:

```text
python scripts/instruction_package_validate.py visualization-contract.json \
  --assembly-contract assembly-contract.json \
  --bom-contract bom-contract.json \
  --frame-manifest frame-manifest.csv \
  --artifact-root release-media
```

The validator resolves every occurrence, BOM mapping, find number, quantity,
view/frame, critical pose, timestamp, configuration, and artifact checksum.

## Gate 1 — Freeze authoritative sources

Record FreeCAD/OpenCASCADE/add-on versions, root FCStd hash, child revisions/hashes, released configuration, occurrence IDs, BOM revision, joint/DOF evidence, collision/clearance report, approved assembly sequence, and units/frames. Open untrusted FCStd files only under the project’s quarantine policy and use current security-maintained FreeCAD builds.

Keep design placements authoritative. Simulation poses and exploded transforms are named derivative view states that must reset without changing the assembled definition.

## Gate 2 — Author a prescribed-motion visualization

In FreeCAD 1.1 native Assembly:

1. Select `Create Simulation`.
2. Add supported driven joints and choose angular/linear motion as applicable.
3. Record each exact `f(time)` formula, units, start/end time, output step, solver error tolerance and playback FPS.
4. Generate the simulation and verify actual joint values at first, last and critical poses.
5. Cold-open/regenerate and compare the pose/frame manifest.

FreeCAD 1.1.2 supports selectable Revolute, Slider and Cylindrical drivers; dependent joints may follow the solved assembly. Verify against the project-pinned version.

Run separate collision/minimum-distance and swept-envelope checks at endpoints, transitions and adaptively refined critical regions. A discrete frame sequence can miss contact. Link, but never infer, the engineering verdict.

## Gate 3 — Capture deterministic frames and media

Freeze projection, camera orientation/position, fit/crop, resolution, background, render style, visibility, transparency, section/clipping state, colors, labels and overlays. Capture numbered lossless PNG frames in a FreeCAD GUI session; preserve time, actual joint values, pose ID, source/configuration hash and image SHA-256 in the manifest.

The native Animation Player is the playback baseline. Do not claim native video export unless the pinned version provides and verifies it. Encode MP4/WebM/GIF only from the audited PNG sequence with a pinned external encoder; keep the PNGs as evidence.

Check frame continuity, count/order, duplicate/missing frames, FPS/duration, first/last/critical poses, camera clipping, occlusion, flicker, legibility and checksum. A high-quality render remains a derivative, not engineering evidence.

## Gate 4 — Create exploded views without corrupting placement

Use native Assembly `Create Exploded View` and store named Normal/Radial Move objects mapped to occurrence IDs and assembly/service steps. Build sub-explodes where sequence requires them. Ensure the design state returns to assembled placement after editing.

Insert the `Exploded_View` into TechDraw. Add connector lines, balloons/find numbers, quantities, orientation arrows, notes and parts list. Reconcile every callout to the controlled BOM, including fasteners and non-geometric consumables.

Validate insertion/removal/tool paths on the assembled engineering model. Do not use explode vectors as proof of feasibility.

## Gate 5 — Build assembly and service instructions

For each step record:

- Step ID, predecessors, configuration, occurrence/find number, quantity and exploded move/view.
- Starting/ending pose, insertion/removal path and orientation.
- Tools, fixtures, torque/angle/preload method, locking compound/adhesive/lubricant, cure and cleanliness.
- Safety, ESD, pinch/lift/energy isolation, PPE and handling notes.
- Inspection/function check, acceptance criteria, rework/reversal limits and quality record.
- Frame/image/TechDraw artifact and caption/localization owner.

Show newly added parts distinctly without relying only on color. Preserve a consistent camera and orientation unless the step intentionally changes it. Support accessibility, print readability and localization.

## Gate 6 — Validate and release derivatives

Release native FCStd with simulation/exploded definitions, source hashes, motion contract, frame manifest and PNGs, encoded media, storyboard/manual, TechDraw source and PDF/SVG, BOM reconciliation, visual QA, tools/versions and checksums.

Any relevant source, configuration, occurrence, BOM, joint, sequence, camera, formula or TechDraw attachment change invalidates affected derivatives until regenerated and reviewed.

Verdicts:

- `PASS — instructional package production candidate`: traceability, sequence, frames, callouts, QA and engineering links pass.
- `DRAFT`: useful visualization without release controls.
- `CONDITIONAL`: exact missing render, language, callout or approval work is listed.
- `FAIL`: stale/missing/misordered derivatives, unresolved BOM links, invalid sequence, or misleading claim exists.

Physical build/function acceptance remains separate.
