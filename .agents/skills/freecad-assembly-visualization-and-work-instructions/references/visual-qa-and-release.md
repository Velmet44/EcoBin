# Visual QA and release

Keep instructional media traceable to the exact engineering definition. Record:

- Root/child/configuration/BOM hashes and generation date.
- FreeCAD, workbench/add-on, capture and encoder versions.
- Motion formulas, sample times, joint values and critical poses.
- Camera projection/matrix, resolution, background and display state.
- Per-frame and final-media hashes, codec/container/FPS and duration.
- TechDraw/PDF/SVG and manual hashes.

Visual review must catch clipped geometry, z-fighting, flicker, false intersections, hidden fasteners, unreadable callouts, ambiguous orientation, inconsistent camera, color-only meaning, missing steps, wrong quantity, stale images, and unsafe instructions.

Retain source PNGs even when a compressed preview is released. Invalidate derivatives after any source/configuration/BOM/sequence/formula/view change.
