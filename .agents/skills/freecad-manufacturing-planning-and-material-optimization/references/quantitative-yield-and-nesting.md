# Quantitative yield, stock, nesting, and remnants

## Keep denominators explicit

Every ratio needs population, configuration, quantity, period, and source. Distinguish:

- geometric nest utilization;
- purchased-to-finished mass utilization;
- first-pass operation yield;
- final accepted yield;
- recycling/recovery fraction;
- disposal fraction.

Do not compare prototype observations with mature production rates without labeling the maturity and uncertainty.

## Material balance

Use one consistent mass boundary:

`purchased = finished + controlled remnant + recyclable scrap + unrecoverable/process loss`

Exclude coolant, fixtures, or added coating from both sides unless the boundary intentionally includes them. If a process adds material, model it as another purchased line.

For machining, report chip mass, bar/plate remnants, workholding tabs, and cleanup allowance. For casting/molding report gates, runners, flash, returns, trim, and rejected parts. For additive report part, supports, coupons, trapped/unrecovered material, refresh material, and rejected builds.

## Layout constraints

Nesting and cutting decisions should preserve:

- material heat/lot and certificate segregation;
- grain/fiber/rolling direction;
- rotation/mirroring restrictions;
- surface quality and protected zones;
- kerf, spacing, heat input, distortion, and common-line risk;
- clamp, chuck, feeder, skeleton, tab, and pickup needs;
- part identification and quantity completeness.

Validate the exported nest or cut geometry in its consuming CAM/process system. Recompute quantity and stock bounds after postprocessing.

## Remnant qualification

A recoverable remnant requires:

- unique ID and material/spec/condition;
- dimensions/mass and usable orientation;
- heat/lot/certificate relationship where required;
- storage location, preservation, inspection/expiry;
- machine-readable availability and future matching rule.

Otherwise classify it as recyclable scrap or disposal, not inventory.

## Standards context

- [ISO 14009:2020](https://www.iso.org/standard/43244.html) gives guidance on material circulation in design and development, including material quantity, life extension, and recovery.
- [ISO 8887-1:2017](https://www.iso.org/standard/62047.html) addresses technical product documentation across manufacture, assembly, disassembly, and end-of-life processing.

Use contractual standards and local environmental/waste rules. This skill does not calculate a life-cycle assessment or establish environmental certification.
