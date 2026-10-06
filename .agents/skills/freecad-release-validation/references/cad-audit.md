# Native CAD and parameter audit

## Deterministic native checks

Record:

- File checksum, size, timestamp, authoring/review versions.
- Document name/label, object count, target Body/solid, and revision metadata.
- Recompute result and every object state.
- Sketch solve status, degree of freedom, full-constraint state, and external geometry count.
- Final shape type, solid/shell/face/edge/vertex counts.
- B-rep validity, closure, volume, area, bounding box, center of mass, and placement.

Run the automated audit, then the FreeCAD GUI Check Geometry with BOP check. The latter can identify self-intersection, too-small edges, nonrecoverable faces, continuity/incompatibility, and invalid curves-on-surface. Use single-threaded mode when required for stability.

Do not “repair” a release by exporting/refining a visibly acceptable copy while leaving the generating feature broken. Fix and revalidate the native tree.

## Independent plausibility checks

Compare CAD output with independent expectations:

- Envelope against interface/control dimensions.
- Volume against a bounding/simple-shape estimate.
- Mass against volume × controlled density, including excluded cavities/components.
- Center of mass against symmetry and load/balance expectation.
- Hole/pattern count and pitch against requirements.
- Minimum wall/ligament/clearance against DFM limits.

Set project-specific numeric acceptance tolerances; do not compare floating-point outputs for exact equality.

## Dependency review

Use Tools → Dependency Graph:

- Arrows should follow valid dependency direction.
- Upward arrows indicate cycles.
- Red links can indicate out-of-scope dependencies.
- A PartDesign Body should have a coherent feature chain.
- External geometry links should be intentional and minimal.

Inspect every generated face/edge dependency that could change after parameter edits. Recompute success does not guarantee the feature still references the intended geometry.

## Parameter sweep design

Test:

- Nominal baseline.
- One-factor lower/upper bounds.
- Coupled extremes that reduce wall, floor, edge distance, clearance, or overlap.
- Values around topology transitions, including just below/at/above when permitted.
- Configurations and discrete branches.
- Manufacturing allowance and tolerance extremes.

Each case should define expected results where possible:

- Valid/invalid by design.
- Solid count.
- Bounding range.
- Volume range.
- Required feature presence/count.
- Fit/clearance inequality.

Declare coverage as `finite_exhaustive` or `sampled`. Only a complete
enumeration whose declared names exactly match the release cases is exhaustive. For continuous parameters,
combine sampled cases with analytical invariants and explicit topology-transition
analysis, or restrict the released configuration set.

Use a fresh document load per case to prevent hidden state. Never save swept values over the source file.

## Visual review

Inspect at least nominal and every topology-changing boundary:

- Section views through thin/deep/internal geometry.
- Transparent or hidden-feature views.
- Seams, sliver faces, tiny edges, self-intersections, and unintended cavities.
- Pattern direction/count and symmetry.
- Datum/interface placement.

Automated shape validity cannot establish semantic correctness.

Source: [FreeCAD Check Geometry](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Part_CheckGeometry.html), [dependency graph](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Std_DependencyGraph.html), and [Sketcher solver states](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Sketcher_Dialog.html).
