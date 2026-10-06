# BOM lifecycle, configuration, and release

## Product structure semantics

Keep these identities separate:

- **Definition:** controlled part number and revision.
- **Occurrence:** one placement or use of a definition in a parent/configuration.
- **Item/find number:** drawing or list cross-reference.
- **View item:** a representation of a definition or occurrence in eBOM, mBOM, as-built, or as-maintained.
- **Serialized instance:** one physical realization.

The same definition can occur many times. Quantity aggregation is a report; it must not destroy occurrence identity where position, reference designator, torque witness, serial tracking, or service history matters.

## View transformation

Every transformation needs provenance:

| Relationship | Example | Required control |
|---|---|---|
| one-to-one | design fastener → issued fastener | revision/configuration/effectivity |
| many-to-one | cut pieces → purchased bar | quantity factor, scrap/yield, router |
| one-to-many | cable design → wire, terminals, labels | quantities, process, approved sources |
| phantom | logical module → operation kit | parent scope, site, operation |
| substitute | released item → unit-specific replacement | deviation, serial/lot scope, test |

Reconcile forward and reverse. Every released target must have an approved source mapping; every applicable source must be consumed, explicitly retained, or excluded with reason.

## Effectivity

Store effectivity as structured domains, not prose alone:

- configuration IDs;
- inclusive serial or lot ranges;
- date/time interval and time zone;
- plant/site or production line;
- customer/region;
- work order or contract.

Normalize identifiers before overlap checks. A configuration-wide alternate and a unit-specific deviation may coexist only when precedence is explicit.

## Where-used and change

Perform where-used against exact revision/configuration baselines. Analyze:

- direct and transitive parents;
- open work orders and WIP;
- on-hand and supplier pipeline;
- tooling, CAM, inspection, test, firmware, labels, manuals, packaging, spares;
- shipped serials and service stock.

Keep proposed, approved, implemented, and verified states separate. Approval does not prove implementation.

## Standards context

- [ISO 10303-239:2024](https://www.iso.org/standard/78832.html) covers product-life-cycle support, multiple product structures, effectivity, predicted/observed states, task planning, and activity history.
- [ISO 7573:2008](https://www.iso.org/standard/43883.html) covers technical product-documentation parts lists.
- [ISO 10007:2017](https://www.iso.org/standard/70400.html) gives configuration-management guidance.
- [ISO 8887-1:2017](https://www.iso.org/standard/62047.html) covers design information across manufacturing, assembly, disassembly, and end-of-life processing.

Use the standards and editions invoked by the product contract. This skill provides workflow guidance and does not establish conformity or certification.

## Release evidence

Archive:

- native and neutral CAD baselines plus hashes;
- per-view BOM exports and schema/version;
- reconciliation and difference reports;
- transformations and effectivity;
- approved-source and alternate qualification records;
- change and where-used reports;
- cost basis and manufacturing-plan version;
- serial/lot genealogy and software manifest;
- deviations/nonconformances;
- named approvals.

Human-readable PDFs or spreadsheets aid review; keep the machine-readable source as the controlled computational record.
