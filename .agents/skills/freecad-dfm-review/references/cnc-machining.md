# CNC milling and turning DFM

## Table of contents

1. Capability basis
2. Setup and workholding
3. Tool access and feature geometry
4. Holes and threads
5. Walls, floors, and distortion
6. Turning-specific review
7. Edge, finish, and secondary operations
8. Screening heuristics
9. Review checklist

## 1. Capability basis

Obtain:

- Machine type, axis count, travels, spindle/through-spindle limits, rotary limits, bar/chuck/collet capacity, and achievable setup repeatability.
- Controller and postprocessor.
- Tool and holder library with actual flute length, neck, shank, gauge length, corner/nose radius, coolant, and stick-out.
- Workholding approach, jaw/clamp/fixture geometry, probing, and datum transfer.
- Material stock form/condition and supplier capability/tolerance statement.

Do not use quoted “standard tolerance” as a design default until the supplier confirms it for this geometry, material, setup count, and volume.

## 2. Setup and workholding

For each setup:

- Identify six-degree-of-freedom location, clamp direction, contact pads, and part stop.
- Ensure clamping does not act through a fragile wall or distort a critical feature.
- Preserve enough stock/fixture tab/soft-jaw engagement for roughing and finishing.
- Confirm tool and holder clearance to vise jaws, clamps, chuck, tailstock, probe, and machine envelope.
- Define datum transfer when critical features cross setups; prefer critical relationships completed in one setup where practical.
- Plan cut-off and the final feature used to hold the part.
- Consider in-process inspection and re-clamping after heat treatment or stress relief.

Model stock and clamps in CAM because FreeCAD CAM does not automatically understand clamping mechanisms.

## 3. Tool access and feature geometry

- Every milled surface needs a tool axis and holder path; every turned surface must be reachable by the tool/nose without chuck or shoulder collision.
- Internal vertical corners inherit cutter radius. Make the radius larger than the selected cutter radius to reduce tool engagement and permit finishing.
- Square internal corners need a distinct process such as broaching, slotting, EDM, additive, or a relief/dogbone accepted by design.
- Deep narrow pockets, grooves, and slots increase deflection, chatter, heat, chip evacuation difficulty, and cycle time.
- Avoid unnecessarily long tool stick-out. Verify flute/neck/shank clearance, not only diameter.
- Provide tool runout/approach for shoulders, grooves, threads, and ground surfaces.
- Avoid tangent/coplanar slivers and knife edges.
- Prefer standard cutter, drill, reamer, tap, insert, and stock sizes when function permits.
- Use through features when they improve chip/coolant evacuation and do not violate function.

## 4. Holes and threads

- Use standard drills for noncritical holes; use boring, reaming, honing, grinding, or other finishing when size/form/finish requires it.
- Check drill point depth below a blind-hole cylindrical depth. Provide chip space and tap lead/runout.
- Distinguish modeled cosmetic threads from product-definition thread callouts and manufacturing geometry.
- State thread standard, nominal size/pitch or TPI, class/tolerance, handedness, depth/through, and insert requirement.
- Check tool access and gauge access. Deep small holes and interrupted holes may need special tooling/process.
- Size thread engagement from load/material and applicable design method; “more depth” does not automatically add strength after the mating member becomes limiting.
- Check minimum ligament and edge distance for bearing, tear-out, tapping, and distortion.
- For intersecting holes/passages, address burrs and cleaning at the intersection.

## 5. Walls, floors, and distortion

- Thin and tall walls deflect under cutting and clamping; thin floors can oil-can or break through.
- Large material removal can release residual stress. Consider symmetric roughing, leaving finish allowance, stress relief, and final machining after stabilization.
- Plastics are especially sensitive to clamping, heat, moisture, creep, and stress relief.
- Abrupt section changes, asymmetric stock removal, heat treatment, and coating can shift geometry.
- Ensure finishing stock remains on critical faces after roughing and any intermediate process.
- Put tight flatness/profile requirements on functionally necessary surfaces, not every broad face.

## 6. Turning-specific review

- Prefer rotationally symmetric geometry and standard stock diameter.
- Check chuck/collet grip, bar protrusion, tailstock/steady-rest need, and slenderness.
- Provide tool runout at shoulders and threads; account for insert nose radius.
- Avoid deep narrow grooves and inaccessible back features.
- Verify internal boring bar diameter, length-to-diameter, chip evacuation, and minimum bore.
- Plan part-off width/location and the residual pip/secondary-face operation.
- Complete coaxial critical diameters in one chucking when possible.
- Specify runout/coaxial relationships to functional datum axes, not vague “concentricity” language.

## 7. Edge, finish, and secondary operations

- State an edge-break range or controlled deburr note; “break all sharp edges” alone can damage sealing, locating, or gauge edges.
- Identify edges that must remain sharp or receive a functional radius.
- Localize surface texture to functional surfaces and confirm the process direction/lay where relevant.
- Include grinding/lapping/honing allowance where used.
- Include coating/plating/mask effects in final dimensions and thread fits.
- Define cleaning, passivation/anodize/plating, heat treatment, marking, and packaging sequence.
- Reinspect characteristics affected by secondary operations.

## 8. Screening heuristics

Use these only to trigger review:

- A vendor example recommends keeping deep slot-like milled features below roughly six times feature width and flags very thin walls; actual limits vary by material, cutter, support, and supplier.
- A vendor example notes deep holes around five to six diameters become more difficult due to chip evacuation.
- A vendor example reports different capability for same-side versus cross-setup feature location.

Do not copy those ratios into a drawing. Ask the selected supplier for current capability.

## 9. Review checklist

- [ ] Named machine/supplier capability
- [ ] Stock and all setups defined
- [ ] Workholding and datum transfer credible
- [ ] Tool and holder reach verified
- [ ] Internal radii match available tools
- [ ] Deep/small/slender features reviewed
- [ ] Holes/threads have tool, chip, and gauge access
- [ ] Walls/floors withstand cutting and clamping
- [ ] Distortion and process sequence addressed
- [ ] Critical relationships kept in stable setup where possible
- [ ] Edge break, burr, cleaning, and finish defined
- [ ] Secondary-operation allowance and reinspection defined
- [ ] CAM clamp/collision review planned

Sources: [FreeCAD CAM limitations](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/CAM_Workbench.html), [Protolabs complex CNC guidance](https://www.protolabs.com/resources/design-tips/mastering-complex-features-on-machined-parts/), [Protolabs tolerance guidance](https://www.protolabs.com/resources/design-tips/fine-tuning-tolerances-for-cnc-machined-parts/), and [Haas part setup](https://www.haascnc.com/service/online-operator-s-manuals/mill-operator-s-manual/mill---part-setup.html).
