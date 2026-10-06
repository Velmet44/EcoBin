# Drawings and exchange artifacts

## TechDraw release review

Add dimensions after the 3D model stabilizes. Projected-edge dimensions remain exposed to topological naming changes.

Check:

- Correct template, sheet size, units, scale, projection method/symbol, view orientation, hidden lines, sections/details, and center marks.
- Title block identity, revision, material/condition, finish, general tolerance, weight if controlled, and approval fields.
- Dimensions attach to the intended features and display actual values after recompute.
- Diameter/radius/hole/thread callouts are unambiguous.
- GD&T frames, datum feature symbols, surface indications, welding/special-process symbols, and notes follow the selected standard and company practice.
- No duplicated, dangling, overlapping, or off-sheet annotations.
- PDF/SVG/DXF export visually matches the source page.

FreeCAD TechDraw can represent manufacturing drawings, but the agent must manually validate semantics. A symbol placed on a page does not prove its standard-compliant application.

## STEP/B-rep exchange

Prefer STEP for solid geometry exchange unless the recipient specifies another B-rep format. Record the selected schema and options.

Validation:

- Export intended final objects only; avoid “select all,” which can include hidden/intermediate objects.
- Confirm units, placement, names, solid count, colors, and assembly structure requirements.
- Reimport into a clean document/application.
- Run validity/BOP checks.
- Compare mass properties and envelope using project-defined tolerances.
- Inspect critical holes, cylinders, threads representations, splines, and trimmed surfaces.

STEP does not carry all FreeCAD history or every drawing annotation. Ship native/history and drawing separately when required.

## DXF

For profiles/flat patterns:

- State units and authoritative plane.
- Validate closed contours, cutouts/islands, layer meaning, line/arc/spline support, and no duplicates/overlaps/gaps.
- Confirm whether the supplier, not CAD, owns bend deduction/K-factor and production flat.
- Add bend/center/etch lines only by agreed layer/process convention.
- Compare flat dimensions and feature locations with the formed-part strategy.

## Mesh

For STL/3MF:

- Define chordal/linear and angular deviation from function and process, not a generic “fine” preset.
- Preserve units explicitly; STL itself commonly lacks reliable unit metadata.
- Verify manifold/watertight state, normals, component count, no self-intersection/degenerate facets, and adequate curved-surface tessellation.
- Reimport and compare envelope/volume within the meshing error budget.
- Verify print orientation, wall/feature minimums, escape/drain holes, and supports in the process plan.

Use 3MF when richer unit/material/build metadata is required and supported, but still verify the recipient workflow.

Sources: [FreeCAD TechDraw](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/en/TechDraw_Workbench.html), [TechDraw dimension limitations](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/TechDraw_LengthDimension.html), and [FreeCAD import/export preferences](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Import_Export_Preferences.html).
