# Standard fasteners

Verify current status before a controlled release. Full standards are copyrighted; use an organization-controlled copy or controlled manufacturer drawing for release-critical dimensions.

## Identify the hardware completely

Record head and drive independently:

| Common request | Engineering interpretation |
|---|---|
| Allen screw | Hexagon-socket drive; head is still unspecified |
| Socket head cap screw | ISO 4762:2004; normally hexagon-socket drive |
| Flat-head Allen screw | Hexagon-socket countersunk head; ISO 10642:2026 is the current metric reference |
| Button-head Allen screw | Hexagon-socket button head; ISO 7380-1:2022 |
| Hex nut | ISO 4032:2023 regular-style nut, subject to the required property class |
| Plain washer | ISO 7089:2000 normal series; confirm status because revision work is active |

Also record metric thread designation/pitch and tolerance, nominal length and its head-dependent measurement convention, thread length, material/property class, finish/coating, locking feature, quantity, and approved manufacturer/part number where supply is controlled.

Useful primary references:

- ISO 4762:2004, hexagon socket head cap screws: <https://www.iso.org/standard/34460.html>
- ISO 10642:2026, hexagon socket countersunk head screws: <https://www.iso.org/standard/90795.html>
- ISO 7380-1:2022, hexagon socket button head screws: <https://www.iso.org/standard/78699.html>
- ISO 4032:2023, regular hex nuts: <https://www.iso.org/standard/75016.html>
- ISO 7089:2000, plain washers: <https://www.iso.org/standard/13666.html>
- ISO 273:1979, fastener clearance holes, confirmed 2024: <https://www.iso.org/standard/4183.html>
- ISO 261:1998 and ISO 965-1:2026 for the metric thread system and tolerances: <https://www.iso.org/standard/4165.html> and <https://www.iso.org/standard/87889.html>
- ASME B18.3 for inch-series socket products: <https://www.asme.org/codes-standards/find-codes-standards/b18-3-socket-cap-shoulder-set-screws-hex-keys>

Do not silently substitute inch ASME geometry for metric ISO hardware. Confirm whether an older DIN callout has been superseded.

## FreeCAD Fasteners Workbench

The external Fasteners Workbench is the preferred current FreeCAD generator for many standard fasteners: <https://github.com/shaise/FreeCAD_FastenersWB>.

For controlled use:

1. Pin and record the version/commit and FreeCAD version.
2. Record the standard and edition separately from the generated object.
3. Verify head envelope, bearing face, drive, thread/nominal diameter, pitch, length, and critical seating geometry.
4. Verify automatic attachment direction and placement.
5. Use its Simplify/static-shape path when recipients do not have the add-on, subject to license review.
6. Keep threads simplified unless detailed thread geometry is functionally necessary.

The add-on’s code license does not establish the redistribution rights of every resulting workflow or source datum. Resolve that question separately.

## Holes and joints

- Define clearance holes from ISO 273 or the project’s controlled standard and functional tolerance.
- Define tapped holes from the exact thread specification, material engagement, tool/runout depth, and process.
- Countersunk screws have reduced loadability under ISO 10642; do not substitute them for cap screws without joint analysis.
- Geometry does not select preload or torque. Record lubrication, coating, prevailing torque, locking, grip, engagement, reuse, and verified torque/preload method in the assembly.
- Never Boolean-subtract a screw model to create its manufacturing hole.
