---
name: freecad-production-bom-and-configuration
description: Build, reconcile, cost, release, and maintain production BOMs and configuration records for FreeCAD products. Use whenever work involves eBOM, mBOM, as-planned, as-built, or as-maintained structures; make/buy decisions; supplier and manufacturer parts; alternates and substitutions; effectivity; where-used; engineering changes; lot or serial traceability; firmware; procurement risk; cost roll-up; service spares; or reconciling CAD occurrences with purchasing and manufacturing records.
---

# FreeCAD Production BOM and Configuration

Runtime compatibility: Codex and Claude Code; Python 3.10+ for deterministic contract validation. FreeCAD is optional for occurrence extraction and required only when CAD data must be inspected.

Treat a BOM as a governed product-life-cycle view, not a spreadsheet copied from visible solids. Geometry identifies some occurrences; it does not identify adhesives, labels, firmware, packaging, process consumables, approved alternates, serial effectivity, or what was actually installed.

This skill prepares production records and checks their internal consistency. It does not approve suppliers, certify regulatory compliance, query an ERP/PLM without authorization, or prove that a physical unit matches its record.

Read:

- `references/bom-lifecycle-and-release.md` for view transformations, effectivity, change, where-used, and release.
- `references/procurement-cost-and-traceability.md` for approved sources, cost, shortages, lot/serial genealogy, firmware, and service data.

Copy `assets/bom-contract.json` and, when a tabular exchange is needed, `assets/lifecycle-bom.csv` into the project. Populate the JSON authority record and run `scripts/bom_contract_validate.py`.

Sentinel policy: use JSON `null` only for fields the schema explicitly permits to be absent. Values such as `TBD`, `unknown`, `N/A`, `none`, `pending`, `?`, and placeholder dates never satisfy a required field. An untouched template is expected to fail until controlled values replace its placeholders.

## Gate 1 — Establish authority and identity

Record:

- Product number, revision, lifecycle state, owner, units, currency, cost basis date, governing configuration procedure, and acceptance-authority role.
- Released configurations, options, regions, customer variants, effectivity, and excluded combinations.
- Stable part number plus revision for every definition; a unique occurrence ID for each placement.
- Which system is authoritative for CAD, eBOM, mBOM, procurement, software, as-built genealogy, and maintenance history.
- Source timestamps/hashes and reconciliation date so stale extracts cannot masquerade as current state.

Do not use filenames, labels, item/find numbers, or supplier descriptions as product identity. Preserve supplier and manufacturer identifiers as attributes, not as substitutes for the internal part number.

## Gate 2 — Model distinct lifecycle views

Maintain explicit views:

1. **eBOM / as-designed** — functional design definitions and occurrences, including non-geometric design items.
2. **mBOM / as-planned** — manufacturing sequence, phantom groups, bulk quantities, kits, process consumables, packaging, fixtures where governed, and make/buy splits.
3. **as-built** — the exact serialized/lot-controlled installed items, approved deviations, rework, firmware, and inspection/build evidence.
4. **as-maintained** — removals, installations, repairs, firmware changes, life-limited status, and current configuration.

Use explicit transformation links between views. For each link record source item, target item, quantity factor, configuration/effectivity, transformation reason, and approval.

Never silently overwrite one view with another. A phantom mBOM group may be correct for planning but is not proof that the eBOM definition disappeared. A substitute in one serialized unit is not an unrestricted design alternate.

## Gate 3 — Reconcile CAD and eBOM

Extract or inspect the recursive FreeCAD occurrence graph by controlled part number and revision. For each configuration:

- Reject duplicate occurrence IDs, unresolved links, stale child revisions, hierarchy cycles, invalid quantities, and configuration leakage.
- Compare CAD occurrence totals to the eBOM, while honoring explicitly excluded reference geometry and non-geometric items.
- Keep independently released parts and purchased components as independent definitions.
- Record make/buy/standard/bulk/consumable/software/firmware/packaging/reference classification.
- Include material, specification, finish, UOM, mass source, reference designator, safety/criticality class, and component record.

A geometry-derived reconciliation must report both classes of difference: CAD occurrences absent from the controlled eBOM and controlled non-geometric items absent from CAD.

## Gate 4 — Build the mBOM and planning links

For each mBOM item record:

- Plant/site, operation or kit allocation, supply type, issue method, scrap/yield factor, order/issue UOM, and quantity rounding rule.
- Phantom, kit, bulk, consumable, packaging, tooling/fixture, or production-test status.
- Source eBOM item(s) and approved transformation rationale.
- Router/operation reference and configuration/effectivity.

Use `../freecad-manufacturing-planning-and-material-optimization/SKILL.md` to establish quantitative stock, yield, process, cycle-time, cost, and waste evidence. Import its approved material and operation totals; do not independently invent a competing cost basis.

## Gate 5 — Govern procurement and alternates

Use `../freecad-component-sourcing/SKILL.md` to create and validate the governed component record, exact manufacturer identity, supplier evidence, source hashes, and authoritative geometry/envelope for each standard or purchased item and proposed alternate. This BOM skill consumes those records and governs where, when, and in what quantity an approved identity may be used. It does not independently re-identify a component or make downloaded/catalog geometry authoritative. The component record is the single source for sourced-component identity and geometry provenance; the lifecycle BOM is the single source for product occurrence, configuration, effectivity, and substitution applicability.

For buy, standard, ECAD, software-bearing, and outsourced items record:

- Internal part/revision, approved manufacturer and manufacturer part number.
- Approved supplier and supplier part number, sourcing status, region/site, lifecycle state, MOQ/order multiple, lead time, and quote validity.
- Unit cost, currency, price-break quantity, freight/duty treatment, and source.
- RoHS/REACH/conflict-mineral or other declarations only where contractually applicable, including document identity and expiry.
- Approved alternates with interchangeability class, restrictions, effectivity, qualification evidence, and approval.

Distinguish:

- **Equivalent alternate** — approved for declared configurations/effectivity without unit-specific deviation.
- **Conditional alternate** — requires stated process, firmware, test, region, or configuration conditions.
- **Substitution/deviation** — unit, lot, order, or time bounded; does not modify the released design.

Never claim interchangeability from matching nominal geometry alone. Check functional, dimensional, material, environmental, electrical, software, safety, regulatory, tooling, and service consequences.

## Gate 6 — Control effectivity and change

Express effectivity using declared, non-ambiguous domains such as date range, serial range, lot, plant, configuration, customer, or work order. Open bounds must be intentional.

For every engineering/manufacturing/service change record:

- Change ID, reason, problem statement, affected definitions/views/configurations, disposition, approval, and implementation state.
- Old/new revision or quantity, transformation impact, stock/WIP disposition, tooling/program/document impact, qualification and inspection impact.
- Backward/forward interchangeability and service effect.
- Where-used results at the revision and configuration level.
- Effectivity cut-in and serial/lot breakpoint.

Reject overlapping contradictory effectivity and changes whose affected parent structures were not analyzed.

## Gate 7 — Cost and supply-risk roll-up

Keep cost categories explicit:

- Direct material/purchase price.
- Conversion/process cost imported from the approved manufacturing plan.
- Outsourced operations, tooling amortization, inspection/test, scrap/rework allowance, packaging, logistics, duty, and non-recurring cost.

State currency, basis date, price-break quantity, batch size, exchange-rate source, burden assumptions, and whether totals are standard, quoted, estimated, or actual.

Calculate extended quantity and cost recursively without double-counting phantom groups, parent-included bulk material, or conversion costs already embedded in a purchased assembly. Report:

- Unit and batch rolled cost.
- Uncosted items and expired quotes.
- Single-source and obsolete/end-of-life exposure.
- Lead-time drivers, MOQ/order-multiple surplus, and approved alternate coverage.
- Cost delta by change/configuration.

An estimate is decision support, not a supplier commitment.

## Gate 8 — Record as-built genealogy

For each serialized or lot-controlled product:

- Product serial/lot, configuration, work order, build date/site, BOM revision/baseline, and disposition.
- Installed part/revision, occurrence, quantity, manufacturer/supplier, supplier lot, internal lot, component serial, date/expiry where applicable.
- Approved deviation/substitution, rework/nonconformance, inspection/test evidence, and operator/approver role.
- Firmware/software component, version, checksum, target hardware, configuration/calibration dataset, load date, and verification evidence.
- Material/process certificates required by the contract.

Traceability depth must follow safety, regulatory, reliability, warranty, and customer requirements. Do not collect personal or supplier-sensitive data without a defined purpose and access control.

The installed part/revision must equal the nominal definition on the referenced occurrence, or be an approved alternate whose structured effectivity covers that unit/configuration/site/date. Any other mismatch requires an explicit approved deviation/substitution record naming the nominal and installed definitions, exact product serial scope, evidence, and human approval. A note on the installed line is not authorization.

## Gate 9 — Maintain the fielded configuration

Record each maintenance event as an immutable transaction:

- Asset serial, date/time, location/organization, reason, work order, and current-hours/cycles where applicable.
- Removed and installed occurrence/part/revision/serial/lot.
- Firmware/calibration change, life-limited counters, inspection/test, deviation, and release-to-service authority.

Derive current as-maintained configuration from the accepted baseline plus ordered transactions. Never erase the as-built record.

## Gate 10 — Validate and release

Run:

```bash
python scripts/bom_contract_validate.py path/to/bom-contract.json
```

For a production candidate, require:

- One released configuration baseline and complete view identities.
- Valid definitions, occurrences, transformations, effectivity, approved sources, costs, and evidence references.
- Reconciliation of eBOM ↔ CAD and eBOM ↔ mBOM.
- Where-used/change impact for released changes.
- As-built records for units claimed built; maintenance history for units claimed field-current.
- Named human approvals with role, scope, date, decision, and configurations.

Release a package containing the contract, human-readable BOMs, source extracts/hashes, reconciliation reports, where-used/change reports, approved-source list, cost roll-up, as-built genealogy, software manifest, deviations, and approvals.

Use verdicts:

- `PASS — BOM production candidate`: internal consistency and declared gates pass; supplier/build authorization remains external.
- `CONDITIONAL`: name exact assumptions, configurations, missing authority, and invalidated claims.
- `FAIL`: identity, hierarchy, transformation, effectivity, source, cost, genealogy, or evidence defects block the claim.
- `RELEASED`: only after the authorized configuration authority approves the baseline.

The validator checks declared JSON consistency. It does not inspect FreeCAD, ERP/PLM/MES data, certificate authenticity, cybersecurity, supplier capability, inventory, or the physical build.
