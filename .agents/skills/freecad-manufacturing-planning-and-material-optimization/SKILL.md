---
name: freecad-manufacturing-planning-and-material-optimization
description: Turn FreeCAD parts and assemblies into quantitative manufacturing plans that minimize material waste and total production cost without weakening engineering requirements. Use for process routers, make/buy and process selection, stock-size optimization, sheet or plate nesting, bar/tube cut plans, machining buy-to-fly, additive build packing and supports, yield/scrap/rework, remnant reuse, cycle and setup time, batch economics, packaging/logistics, break-even analysis, or production material/cost reporting.
---

# FreeCAD Manufacturing Planning and Material Optimization

Runtime compatibility: Codex and Claude Code; Python 3.10+ for deterministic plan validation. FreeCAD is required only when geometry, CAM stock, Path operations, or measured part properties must be inspected.

Optimize the complete production route, not a single attractive utilization percentage. A tight nest can increase heat distortion, handling, common-line risk, or inspection failures. A near-net blank can reduce chips yet increase supplier lead time, minimum order, or datum uncertainty.

This skill creates a quantitative decision record. It does not quote a supplier, prove machine capability, simulate every process, certify environmental claims, approve a release, or authorize shop-floor work.

Read:

- `references/quantitative-yield-and-nesting.md` for mass balance, utilization, stock optimization, nesting/cut planning, additive material, remnants, and waste.
- `references/router-cost-and-production-risk.md` for process routers, cycle/cost models, capacity, quality loss, packaging, alternatives, and release evidence.

Copy `assets/manufacturing-plan.json` and `assets/material-yield-register.csv` into the project. Populate the JSON authority record and run `scripts/manufacturing_plan_validate.py`.

The template returns `DRAFT`. Production plans must conserve input/good/scrap
quantity and state across the router, reconcile layout inputs and finished mass,
declare separate machine/labor setup time, end in one accepted terminal batch equal
to the product batch quantity, and calculate cost per accepted unit.

Sentinel policy: use JSON `null` only for fields the schema explicitly permits to be absent. Values such as `TBD`, `unknown`, `N/A`, `none`, `pending`, `?`, and placeholder dates never satisfy a required field. An untouched template is expected to fail until controlled values replace its placeholders.

## Gate 1 — Freeze requirements and planning basis

Record:

- Part/assembly number and revision, configuration, maturity, annual and batch quantity, lot strategy, plant/supplier region, currency, cost basis date, units, and acceptance-authority role.
- Released geometry/source hash and the exact manufacturing drawing, material, heat treatment, finish, special-process, GD&T, cleanliness, and inspection revisions.
- Functional datums, critical characteristics, protected surfaces, grain/fiber direction, cosmetic zones, contamination controls, and traceability requirements.
- Demand profile, target takt/capacity, expected mix, prototype versus production intent, and approved assumptions.

Never optimize away a requirement silently. List each proposed tolerance, material, finish, process, or geometry relaxation as an engineering change requiring authority.

## Gate 2 — Create candidate process routes

Describe the state transition from purchased stock to accepted, packed product:

1. Stock receiving and certificate/lot verification.
2. Primary separation, forming, printing, casting, forging, molding, or rough machining.
3. Datum creation and stable workholding.
4. Intermediate machining/forming, stress relief or heat treatment, deburr/clean.
5. Special processes and finishing with allowance/masking.
6. Inspection/test gates and nonconformance path.
7. Marking, preservation, packaging, and shipment.

For every operation record sequence/predecessors, input and output state, site/work center, setup, machine, tooling/fixture, parameters under process authority, quantity/yield, time, cost rates, inspection, evidence, and special-process qualification.

Separate process planning from NC authorization. Use `../freecad-cam-planning/SKILL.md` for executable CAM, machine limits, simulation, posting, and shop prove-out.

## Gate 3 — Choose stock and preform quantitatively

Evaluate standard and supplier-available stock forms before custom stock:

- Sheet/plate thickness, bar/tube/extrusion section, casting/forging/molded preform, additive build volume, and purchased component blank.
- Purchased tolerance, straightness/flatness, mill edge, scale/decarburization, grain direction, heat/lot size, certificate, MOQ/order multiple, lead time, and remnant policy.
- Setup and clamping allowance, saw/laser/waterjet kerf, facing/cleanup, workholding tabs, machining envelope, thermal distortion, finish/coating, and supplier variation.

Report the smallest feasible standard-stock candidate and at least one credible alternative when material or conversion cost is significant. A stock envelope is feasible only after datums, clamping, tool reach, cleanup, distortion, and inspection are considered.

## Gate 4 — Close the material balance

For each material/stock line and batch record:

- Purchased quantity and mass.
- Accepted finished-part mass.
- Recoverable remnant mass.
- Recyclable segregated scrap/chip/powder mass.
- Process loss such as oxidation, evaporation, contamination, mixed waste, or unrecovered powder.
- Measurement/calculation source and uncertainty.

Require:

`purchased mass = finished mass + recoverable remnant + recyclable scrap + unrecoverable/process loss`

Calculate:

- Material utilization = finished mass / purchased mass.
- Total recoverable fraction = (remnant + recyclable scrap) / purchased mass.
- Buy-to-fly or buy-to-finished ratio = purchased mass / finished mass.
- Waste to disposal = unrecoverable/process loss / purchased mass.

Do not call recyclable chips “zero waste.” Record recovery route, contamination, ownership, transport, value/credit, and evidence.

## Gate 5 — Optimize sheet, plate, bar, tube, and additive layouts

For sheet/plate nesting record:

- Stock size, usable margins, clamp/no-cut zones, kerf, common-line policy, minimum web/thermal spacing, lead-in/out, micro-joints/tabs, grain direction, rotation/mirroring restrictions, part mix, and remnant threshold.
- Quantity completeness, part IDs/revisions/configurations, nest algorithm/version/seed, and exported geometry/toolpath evidence.

For bar/tube cut plans record:

- Stock length, end trim, saw/part-off kerf, chuck/feeder/drop length, cut sequence, quantity, minimum reusable remnant, bundle/heat traceability, and defect zones.

For additive builds record:

- Usable build volume, orientation, packing clearance, support volume, anchors/rafts, purge/qualification coupons, recoater/thermal risk, powder/polymer batch, refresh/reuse rules, and post-process yield.

Calculate geometric utilization independently from mass utilization when density, supports, mixed materials, coating, or powder refresh makes them differ. Save the actual nest/cut/build artifact; a declared utilization value does not prove geometry feasibility.

## Gate 6 — Plan remnants and circular material flow

Give every qualifying remnant a unique record with material/spec, heat/lot, dimensions/mass, geometry file or photo, location, date, condition, certificate linkage, prohibited use, and expiry/reinspection rules.

Define:

- Minimum remnant dimensions/value for inventory.
- Matching rules for future jobs.
- FIFO/expiry and segregation controls.
- Chip/scrap sorting, coolant/contamination limits, recovery vendor, and credit basis.
- Product disassembly/reuse/recovery considerations where within scope.

Do not count a remnant as recoverable if no controlled identification, storage location, feasible future use, or disposition route exists.

## Gate 7 — Quantify yield, rework, time, and capacity

For each operation and batch:

- Input quantity = good output + scrap.
- Rework quantity is a subset of input; record additional rework time/cost and the final disposition.
- First-pass yield = (good output − reworked output) / input.
- Final yield = good output / input.
- Rolled throughput yield uses the declared sequence and consistent population; do not multiply unrelated samples.

Separate:

- Setup and changeover time.
- Machine cycle time per input unit.
- Direct labor time per input unit.
- Inspection/test time per batch.
- Queue, move, cure, thermal, outsource, and calendar lead time.

Capacity must account for shifts, uptime/OEE basis, maintenance, changeovers, mix, bottlenecks, and constrained resources. Stopwatch observations, CAM estimates, supplier quotes, and planning standards are different evidence classes.

## Gate 8 — Build a transparent cost model

Calculate by batch and accepted unit:

- Purchased material less controlled scrap/remnant credit.
- Direct labor and machine time.
- Consumables, cutters/tool life, fixture/tooling amortization.
- Outside/special processes.
- Inspection/test, rework, expected scrap, packaging, freight/logistics, duty, and disposal.
- Non-recurring engineering/tooling separately from recurring cost.

State currency, basis date, quantity, yield, burden, energy, quote validity, and uncertainty/range. Missing values remain missing; do not convert them to zero.

Export approved conversion/material values to `../freecad-production-bom-and-configuration/SKILL.md` for product cost roll-up.

## Gate 9 — Compare alternatives and sensitivities

Compare credible routes at the same accepted quantity and requirement set, for example:

- billet machining versus near-net casting/forging;
- laser/waterjet/punch versus machining;
- standard plate versus extrusion;
- additive versus subtractive;
- manual fixture versus dedicated fixture/automation;
- in-house versus qualified outsource.

Include tooling/NRE, MOQ, yield ramp, lead time, capacity, quality risk, supply risk, change flexibility, inspection, logistics, and end-of-life. Calculate break-even quantity only from explicit fixed and variable costs. Run sensitivity on uncertain drivers such as yield, cycle time, material price, demand, tool life, and scrap credit.

Do not choose solely by unit cost. Identify Pareto tradeoffs and the authority making the decision.

When no second route is technically or commercially credible, record a structured `no_alternative_justification` rather than fabricating a comparison. It must state the reason and scope, summarize alternatives screened out, name the approving human and role, carry an ISO date and configuration, link evidence, and have decision `approved`. Revisit it when quantity, requirements, suppliers, material, or process capability changes.

## Gate 10 — Package, verify, and release

Run:

```bash
python scripts/manufacturing_plan_validate.py path/to/manufacturing-plan.json
```

For a production candidate require:

- Source-controlled requirements and at least one complete router.
- Closed material balances and evidenced nest/cut/build plans.
- Operation quantity/yield closure and no impossible rework counts.
- Transparent time, cost, packaging, remnant, and disposal records.
- Alternative/sensitivity review for economically significant choices, or a structured approved no-alternative justification.
- Inspection, special-process, supplier, and shop prove-out evidence appropriate to risk.
- Named human approval with role, scope, date, configuration, and decision.

Release the plan, stock/preform decision, router/travelers, nest/cut/build artifacts, setup and inspection plans, material/yield/cost reports, remnant records, alternative/sensitivity analysis, assumptions, deviations, source hashes, and approvals.

Use verdicts:

- `PASS — manufacturing plan production candidate`: declared quantitative gates pass; shop/supplier authorization remains external.
- `CONDITIONAL`: state exact quantity/configuration, assumptions, missing evidence, and affected claims.
- `FAIL`: requirement, stock, material-balance, route, yield, capacity, cost, packaging, or evidence defect blocks the claim.
- `RELEASED`: only after authorized manufacturing and design/quality approvals.

The validator checks declared arithmetic and references. It does not verify nest geometry, CAM paths, machine safety, supplier capability, physical inventory, environmental impact, quote validity, or accepted hardware.
