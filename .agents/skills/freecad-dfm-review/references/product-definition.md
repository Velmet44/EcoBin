# Product definition, tolerancing, and inspection

## Choose one governing system

State the exact revision of the chosen system:

- ASME example: Y14.5-2018 (reaffirmed 2024) plus applicable Y14 drawing/model practices.
- ISO GPS example: ISO 8015 fundamentals with the applicable dimension, geometry, datum, surface, edge, and thread standards.

Do not mix ASME and ISO defaults casually. When a customer/company drawing standard governs, cite it and resolve conflicts.

Check standards status at release time. In July 2026:

- ISO 2768-1:1989 remained published but was expected to be replaced by a new ISO 2768 edition under publication.
- ISO 2768-2:1989 was withdrawn; ISO 22081:2021 covers general geometrical and size specifications in the GPS system.
- ISO 1302:2002 was withdrawn; ISO 21920-1:2021 covered surface-texture indications and was itself under revision.
- ISO 965-1:2026 was the current metric screw-thread tolerance principles edition.

Do not reconstruct proprietary standard tables from memory. Use licensed/current source text where required.

## Functional tolerancing workflow

1. Define the assembly or performance requirement.
2. Select repeatable functional datum features and constrain required degrees of freedom.
3. Identify critical features and tolerance stacks.
4. Select size, form, orientation, location, profile, or runout control that communicates the function without redundancy.
5. Allocate tolerance based on function, process capability, and measurement uncertainty.
6. Confirm material-condition modifiers and datum mobility match assembly behavior.
7. Map every CTQ to a feasible inspection method and sampling/FAI plan.

Avoid:

- Coordinate tolerancing that creates ambiguous rectangular zones when position/profile is intended.
- Using flatness to control orientation or location.
- Applying geometric controls to a datum-free requirement that actually depends on assembly.
- Tight default tolerances on nonfunctional geometry.
- Duplicate or contradictory dimensions.
- Reference dimensions treated as acceptance requirements.

## Fits and threads

- Use ISO 286 or the governing fit system for cylindrical/parallel feature-size fits, after checking temperature, lubrication, finish, roundness, and assembly method.
- Use the current thread standard for profile/series and tolerance/class; state coating/plating allowance and gauging condition.
- Analyze worst-case or statistical stack according to the program’s policy.
- Separate nominal CAD size from product tolerance unless a deliberate limit-state/interference model is being created.

## Surface texture and edges

- Specify surface texture only where it controls sealing, friction, wear, fatigue, coating, appearance, or another requirement.
- State the applicable surface standard, parameter, limit, filtering/evaluation details where needed, and lay/process restriction.
- Define edge condition in a measurable way and exclude functional sharp/sealing/datum edges from blanket notes.

## Inspection feasibility

For each characteristic specify:

- Requirement and revision.
- Datum simulation and setup.
- Instrument/method, range, resolution, access, and environmental controls.
- Measurement uncertainty adequate for the decision rule.
- Sampling, first article, or 100% inspection requirement.
- Post-process state (as-machined, heat-treated, coated, assembled).

A dimension that cannot be accessed or unambiguously set up is not production-grade product definition.

Sources: [ASME Y14.5](https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensioning-tolerancing/2018), [ISO 8015](https://www.iso.org/standard/55979.html), [ISO 1101](https://www.iso.org/standard/66777.html), [ISO 22081](https://www.iso.org/standard/72514.html), [ISO 286-1](https://www.iso.org/standard/45975.html), [ISO 965-1:2026](https://www.iso.org/standard/87889.html), and [ISO 21920-1](https://www.iso.org/standard/72196.html).
