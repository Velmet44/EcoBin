# DFM for other manufacturing processes

## Table of contents

1. Sheet metal
2. Additive manufacturing
3. Injection molding
4. Casting and forging
5. Hybrid and secondary operations

## 1. Sheet metal

Use a sheet-metal-aware model and confirm the FreeCAD SheetMetal add-on/version when a flat pattern is required.

Review:

- One consistent gauge/material condition per formed blank.
- Grain direction, bend direction, minimum bend radius, bend angle, tooling, air/bottom/coining method, and springback.
- Supplier-specific K-factor or bend table. Do not treat a generic CAD default as production calibration.
- Minimum flange length for the selected die opening/tooling.
- Bend relief, corner relief, hems, joggles, seams, and closed-shape tool access.
- Hole/slot/insert distance from bends and edges; features near bends can distort.
- Press-brake collision and bend sequence.
- Flat-pattern overlap, cut kerf, common-line/tabs, burr direction, and protective film.
- Weld/rivet/PEM hardware access, minimum edge distance, heat distortion, and finishing.
- Tolerances after multiple bends; do not apply machined tolerances to formed geometry without a secondary operation.

A vendor screening rule uses roughly four material thicknesses between features and bends, but actual distance depends on material, thickness, radius, and tooling. Supplier bend data governs.

Sources: [bend-radius and K-factor guidance](https://www.protolabs.com/resources/design-tips/the-basics-of-bend-radii-in-sheet-metal/) and [sheet-metal design guidelines](https://www.protolabs.com/services/sheet-metal-fabrication/design-guidelines/).

## 2. Additive manufacturing

Identify the exact process (FDM/FFF, SLA, SLS, MJF, material extrusion, binder jet, metal PBF, etc.), machine, material, build parameters, orientation, and quality level.

Review:

- Build envelope including supports, recoater/thermal constraints, and nesting.
- Orientation effects on anisotropy, surface staircase, supports, warpage, accuracy, and CTQ location.
- Minimum supported/unsupported wall, pin, hole, slot, gap, and text for the selected process.
- Overhang/self-support angle and support access/removal.
- Powder/resin removal, drain/escape holes, trapped cavities, cleaning, and inspection.
- Thermal mass transitions, residual stress, build-plate attachment, heat treatment, HIP, stress relief, and support-removal distortion.
- Machining stock on datums, sealing faces, bores, threads, and other precision interfaces.
- As-built versus machined dimensions and the sequence of heat treatment/coating.
- Lattice validation, minimum strut, enclosed defect detection, and repair/inspection strategy.
- Mesh chordal/angular deviation and watertight/manifold export.

Do not use a single “3D-printing tolerance.” Published capability changes by process, axis/orientation, material, size, and geometry. Obtain supplier data and plan first-article measurement.

Sources: [ISO/ASTM 52910:2018](https://www.iso.org/standard/67289.html), [process-dependent tolerance guidance](https://www.protolabs.com/resources/design-tips/3d-printing-tolerances/), and [NIST powder-bed-fusion activity model](https://nvlpubs.nist.gov/nistpubs/ams/NIST.AMS.100-60.pdf).

## 3. Injection molding

Identify resin/grade, shrink data, mold material/life, cavity count, parting direction, gate/ejection concept, texture, and molder capability.

Review:

- Uniform nominal wall and gradual transitions; core out thick masses.
- Ribs and bosses sized relative to adjacent wall to reduce sink/voids.
- Draft on all faces parallel to mold opening, increased for texture and depth.
- Parting line, shutoffs, undercuts, side actions/lifters, and tool access.
- Gate location, flow length, weld/knit lines, vents, air traps, and cosmetic zones.
- Ejector support and marks, stripping loads, and part retention on the correct mold half.
- Inside/outside radii, steel-safe changes, mold polishing, and insert molding.
- Shrink/warpage/creep/moisture conditioning and fiber orientation.
- Tolerance capability after shrink and the need for post-machining or gauging.

Never apply a universal draft angle or wall thickness. Vendor guidance may suggest typical starting ranges, but resin, texture, depth, tool construction, and geometry govern. Require molder DFM and, for consequential parts, mold-flow/warpage evidence.

Sources: [molding draft guidance](https://www.protolabs.com/resources/design-tips/improving-part-moldability-with-draft/), [uniform wall guidance](https://www.protolabs.com/resources/design-tips/improving-part-design-with-uniform-wall-thickness/), and [molding process guide](https://www.protolabs.com/resources/guides-and-trend-reports/injection-molding-guide-process-design-tips-materials/).

## 4. Casting and forging

Identify alloy, process (sand/investment/die/permanent mold; open/closed-die forging), production volume, die/mold strategy, and machining allowance.

Review:

- Parting line, draw direction, draft, cores, core prints, slides, and trapped tooling.
- Uniform sections and gradual transitions to reduce hot spots, porosity, shrink, laps, and cracking.
- Generous radii/fillets and realistic minimum section.
- Gates/risers/vents/overflow or forging flash land and material flow.
- Machining pads, datum targets, cleanup allowance, stock variation, and fixture location.
- Expected distortion, heat treatment, straightening, surface scale, and defect acceptance.
- Nondestructive examination and sectioning/first-article strategy.
- Grain flow for forging and load path alignment.

Use ASME Y14.8 or the selected ISO/company practice for cast/forged/molded product definition. Require foundry/forge review and process simulation when risk warrants.

## 5. Hybrid and secondary operations

When a part mixes processes:

- Assign dimensional ownership at each stage.
- Define intermediate datums and stock/finish allowance.
- Account for datum loss, distortion, and surface changes.
- Reinspect after the operation that can alter a CTQ.
- Keep as-cast/as-printed/as-formed geometry distinct from final machined geometry and drawing requirements.
