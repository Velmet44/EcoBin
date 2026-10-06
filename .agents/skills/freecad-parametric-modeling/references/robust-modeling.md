# Robust FreeCAD modeling

## Table of contents

1. Coordinate and datum architecture
2. Feature-tree architecture
3. Stable references
4. Sketch design
5. Parameters and dependencies
6. Kernel-sensitive geometry
7. Part families and revisions
8. Review checklist

## 1. Coordinate and datum architecture

Orient the model around function, manufacturing, and inspection:

- Put a stable primary mounting, parting, stock, or inspection plane on an origin plane when practical.
- Align a principal axis of turned parts with the chosen machine/part axis.
- Use datums to encode functional offsets and axes; do not create them merely to imitate a generated face.
- Maintain consistent handedness and document projection/build/tool direction.
- Keep assembly placement outside the internal Body feature coordinate scheme when possible.

Datum features should be physically simulatable in inspection. A mathematical origin without a realizable surface/axis does not define how a part will be set up.

## 2. Feature-tree architecture

A robust tree usually reads from stable/global to local/detail:

1. Metadata and parameters
2. Origin, datums, master/interface sketches
3. Base volume
4. Primary functional geometry
5. Secondary geometry
6. Repeated features
7. Process relief
8. Fillets, chamfers, edge breaks
9. Reporting and drawing objects

Avoid long chains of features that depend on a detail created immediately before them. Group features by function and keep high-fan-out references early and stable.

Use symmetric or mid-plane operations when symmetry is design intent. Avoid “up to face” targets that can disappear or split; use a datum or derived dimension when it represents the requirement more faithfully.

## 3. Stable references

FreeCAD 1.0+ improves topological naming, but generated faces and edges may still change identity after feature edits. Reduce exposure:

- Best: Body origin plane/axis, explicit datum, master sketch, named parameter.
- Good: whole-object binder or stable sketch geometry.
- Riskier: generated face/edge/vertex from a changing solid.

If a generated face is unavoidable:

1. Isolate it in a binder or dedicated feature.
2. Name the functional intent in a note/property.
3. Record the geometric selection criterion.
4. Exercise upstream parameter limits that alter topology.
5. Inspect the downstream feature, not only recompute status.

TechDraw dimensions attached to projected edges can also break after topology changes. Add final drawing dimensions after model stabilization and re-check them after every revision.

## 4. Sketch design

- Use construction geometry for axes, pitch circles, symmetry, and reference envelopes.
- Prefer geometric constraints before dimensional constraints.
- Use named driving constraints for requirements and reference constraints for reporting.
- Avoid redundant dimensions and broad `Block/Fix` constraints that obscure intent.
- Avoid B-splines for prismatic mechanical profiles unless the surface requirement truly needs them.
- Ensure closed profiles have no overlaps, duplicate elements, zero-length segments, or self-intersections.
- Keep external geometry deliberate and minimal.

After solve, require `FullyConstrained == True`, no conflicts/redundancies, and the expected number of wires/faces before consuming a profile.

## 5. Parameters and dependencies

Classify:

- **Independent input** — directly controlled requirement.
- **Derived input** — equation from independent inputs.
- **Reference output** — measured from geometry; never drives the same dependency chain.
- **Configuration choice** — enum or discrete branch.
- **Manufacturing parameter** — stock, allowance, tool radius, bend/shrink factor; assigned by the responsible discipline.

Use input and report spreadsheets separately because FreeCAD dependency tracking can reject or obscure cycles when a sheet both drives and reads the same model.

Keep meaningful parameter bounds and inequalities, for example:

- `hole_diameter > 0`
- `edge_distance >= hole_diameter / 2 + minimum_ligament`
- `pocket_depth < body_thickness - minimum_floor`
- `fillet_radius < adjacent_feature_limit`

Validate before creating features.

## 6. Kernel-sensitive geometry

Watch for:

- Coplanar/tangent Boolean contacts and zero-thickness results.
- Very small edges/faces relative to model scale and tolerance.
- Fillet/chamfer chains crossing changing topology.
- Loft profiles with incompatible segmentation or orientation.
- Sweeps with discontinuous paths or self-intersection.
- Thin-wall/thickness operations around tight curvature.
- Patterns whose instances merge, touch tangentially, or exit the base solid.

Prefer intentional overlap over exact tangent contact in additive Booleans when design allows. For subtractive tools, extend through the target rather than stopping exactly on a face when the requirement is “through.”

Use Part → Check Geometry with BOP check for release candidates. FreeCAD does not automatically repair failed B-reps; correct the generating feature.

## 7. Part families and revisions

- Keep configuration logic explicit; avoid parameter ranges that change the fundamental topology without a planned branch.
- Split distinct topology families into configurations or generators.
- Preserve stable feature names and parameter semantics across revisions.
- Compare mass properties, envelope, interface geometry, and neutral-file reimport after a change.
- Re-run every dependent drawing, DFM, CAM, inspection, and analysis check.

## 8. Review checklist

- [ ] One intended solid per Body
- [ ] Origin/datum scheme matches function, process, and inspection
- [ ] All driving dimensions named and unit-bearing
- [ ] One source of truth per requirement
- [ ] Production sketches fully constrained
- [ ] No unexplained generated topology dependencies
- [ ] No cycles or out-of-scope links
- [ ] Base and high-fan-out features stable
- [ ] Dress-up features late and separated by intent
- [ ] Nominal and boundary cases recompute
- [ ] Final B-rep passes validity and BOP checks
- [ ] Solid count, mass properties, and envelope are plausible
- [ ] Design calculations and assumptions are traceable
