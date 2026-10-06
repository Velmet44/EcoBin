# BOM, exploded views, and assembly release

## Product structure

ISO 10007:2017 provides configuration-management principles: <https://www.iso.org/standard/70400.html>. Freeze definitions, versions, parent-child relationships, occurrences, configurations/effectivity, and approvals.

Distinguish:

- Definition identity: part number plus revision/configuration.
- Occurrence identity: unique placement in the hierarchy.
- Item/find number: drawing/BOM callout, not definition identity.
- State: as-designed, as-planned, as-built, and as-maintained where required.
- Type: make, buy, standard, bulk, consumable, software/firmware, and reference.

ISO 7573:2008 and ISO 6433:2012 cover parts-list information and part references:

- <https://www.iso.org/standard/43883.html>
- <https://www.iso.org/standard/51527.html>

Reconcile recursive occurrence count, not only graphical objects. Include non-geometric adhesives, lubricants, wire, labels, packaging, and installation consumables.

## Exploded and assembly views

Native FreeCAD exploded views can feed TechDraw. Store exploded transforms separately from design placement. For every revision:

- Verify the correct configuration and state.
- Verify separation directions and connector lines.
- Reconcile balloons/find numbers with the released BOM.
- Render and visually inspect PDF/SVG.
- Confirm the written assembly/service sequence; an attractive explode is not path proof.

The sequence must include predecessor dependencies, insertion/removal path, tool/fixture/hand access, torque/preload/locking, adhesives/lubricants/cure, inspection, rework, ESD/cleanliness, replaceable items, and safety cautions.

## Release package

Include:

- Root FCStd and exact child file revisions/hashes.
- Configuration/effectivity matrix and controlled recursive BOM.
- Component provenance records and permitted redistribution disposition.
- Joint/DOF and grounding record.
- Interface/fit/tolerance stack and clearance/contact allowlist.
- Motion/collision/service/tool-access evidence.
- Fastener joint register.
- Mass/CoG/inertia report.
- Assembly and exploded drawings, written sequence, and rendered QA.
- ECAD interface record, board revision/hash, transform, and missing-model disposition.
- STEP export/reimport comparison, manifest, deviations, and approvals.

Hashing proves file identity, not that derived files were regenerated from the correct source. Bind each derivative to the source assembly hash and configuration in its generation/audit record.
