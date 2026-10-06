# Assembly verification

## Constraint and motion evidence

For each configuration capture:

- Grounding strategy and connected occurrence graph.
- Joint type, stable datum references, expected constrained motion, remaining DOF, home, and limits.
- Cold-open/recompute/solve result and any redundancy/conflict diagnostics.
- Endpoint, transition/singularity, and operating-pose tests.
- Pair-specific intentional-contact allowlist.
- Solid-intersection and minimum-distance results with tolerance/environment-adjusted acceptance.
- Sampling step/refinement method and residual risk.

Solver success does not mean physical fit. A CAD joint does not mean contact, friction, preload, stiffness, or a structural load path.

## Fits and tolerance stacks

Useful controlling references include:

- ISO 286-1:2010 and ISO 286-2:2010: <https://www.iso.org/standard/45975.html> and <https://www.iso.org/standard/54915.html>
- ISO 5459:2024 datums: <https://www.iso.org/standard/87855.html>
- ISO 2692:2021 maximum/least material requirements: <https://www.iso.org/standard/74592.html>
- ISO 1101:2017 geometric tolerancing: <https://www.iso.org/standard/66777.html>
- ASME Y14.5-2018 (R2024) as an alternative system: <https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensioning-tolerancing/2018>

Use one declared system. Calculate worst-case assembly by default. RSS or Monte Carlo requires justified distributions, correlation/capability, sample size/convergence, and an acceptance rule. Include coatings, thermal range, load/vibration/centrifugal deflection, wear, lubrication/sealing, flexible items, and full adjustment.

## Threaded joints

The fastener geometry record is only the start. Record joint stiffness/load, separation/slip/fatigue/strip checks, grip and engagement, bearing surfaces, preload range, torque or tensioning method, friction/lubrication/coating state, locking, prevailing torque, installation/tool access, witness/inspection, and reuse.

References:

- NASA-STD-5020B threaded fastening systems: <https://standards.nasa.gov/standard/nasa/nasa-std-5020>
- ISO 16047 torque/clamp force testing: <https://www.iso.org/standard/27788.html>
- ISO 898-1 property classes and its scope limits: <https://www.iso.org/standard/60610.html>

Catalog torque is not automatically approved torque.

## Mass properties

Require a valid material/density or controlled supplier/measured mass for every contributing definition. Report total mass, center of gravity, and inertia tensor in a declared frame for every configuration and key pose. Track uncertainty and overrides. CAD-calculated mass is not measured mass.

## Physical tests

CAD verification and as-built verification are separate. Record physical critical fits/clearances, fastener torque/locking witness, motion and stop behavior, service access, harness behavior, mass, functional tests, inspection uncertainty, and nonconformance disposition.
