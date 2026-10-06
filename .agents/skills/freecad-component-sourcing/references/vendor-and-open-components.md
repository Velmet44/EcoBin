# Vendor and open component models

## Trust hierarchy

An exact manufacturer model plus current drawing is preferred. Supplier CAD is secondary evidence; community libraries are discovery and layout sources until independently verified.

FreeCAD resources:

- Fasteners Workbench: <https://github.com/shaise/FreeCAD_FastenersWB>
- FreeCAD Parts Library: <https://github.com/FreeCAD/FreeCAD-library>
- BOLTS: <https://boltsparts.github.io/> and legacy FreeCAD package <https://github.com/boltsparts/boltsfc>

The FreeCAD Parts Library is community-maintained and CC-BY 3.0. Preserve attribution and verify identity, units, origin, revision, source drawing, solids, and critical dimensions. BOLTS is useful as a pinned fallback but its FreeCAD integration is older; runtime-test it against the project FreeCAD release.

## Supplier terms are engineering inputs

Do not infer that “download” means “redistribute” or that a supplier model contains manufacturing tolerances.

- MISUMI warns that CAD can differ in tolerances, finish, chamfers, and other details: <https://us.misumi-ec.com/contents/terms/use.html>
- McMaster-Carr restricts retention/redistribution and says manufacturing tolerances may be omitted: <https://www.mcmaster.com/termsandconditions>
- 3D ContentCentral limits use and does not warrant accuracy: <https://www.3dcontentcentral.com/Terms-of-use.aspx>
- TE product pages instruct designers to use the product drawing for design activity: <https://www.te.com/en/product-2178531-2.html>
- Samtec describes models as form/fit aids and keeps the product print authoritative: <https://www.samtec.com/support/3dmodels/>

Store restricted sources in access-controlled incoming storage. Release only the permitted normalized representation, or require the recipient to fetch the source under its own agreement. Record the decision.

## Verification checklist

- Exact manufacturer/order code, option string, and revision.
- Untouched source and SHA-256.
- Unit and 1:1 scale.
- Correct handedness, origin, placement, and coordinate system.
- Expected solid count and valid geometry.
- Envelope and interface dimensions against the current controlled drawing.
- Material/mass metadata origin; no guessed density presented as supplier data.
- Light versus detailed representation equivalence at interfaces.
- Lifecycle/obsolescence and approved-alternate status.
- Attribution, license, confidentiality, export, and redistribution disposition.
