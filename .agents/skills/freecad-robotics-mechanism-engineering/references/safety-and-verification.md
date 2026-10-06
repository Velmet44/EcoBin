# Robot mechanism safety and verification

Start with the project’s lifecycle risk assessment. For machinery, ISO 12100:2010 provides general risk-assessment and risk-reduction principles and remained current after its 2022 confirmation, though revision work exists. Industrial robots and applications/cells are addressed separately by ISO 10218-1:2025 and ISO 10218-2:2025. Confirm scope, edition, regional adoption and application-specific requirements with the responsible safety professional.

Do not claim that a mechanism calculation establishes functional-safety performance, regulatory conformity or certification.

## Hazardous mechanism states

Evaluate normal motion, teaching/setup, automatic operation, maintenance, cleaning, recovery, jam release, payload/tool change, transport, gravity loading, stored energy, drive/brake/encoder/control fault, power loss/restoration and foreseeable misuse.

Examples include crushing/shearing, impact, ejection, dropped payload, unexpected motion, inaccessible release, thermal burn, cable/pressure release, sharp/broken parts and instability.

## Verification ladder

1. Review requirements, assumptions, equations and source data.
2. Independently check FreeCAD structure, datums, limits, collisions, clearances and cable envelopes.
3. Verify kinematic/dynamic/structural/thermal models and convergence or sensitivity.
4. Bench-test actuators, transmissions, brakes, sensors and thermal duty.
5. Test subassemblies under bounded loads and fault states.
6. Validate the integrated mechanism and application in the controlled environment.
7. Inspect production units and monitor drift, wear and field changes.

## Required safety evidence

- Hazard/risk-assessment ID and configuration.
- Risk-reduction measure hierarchy and verification method.
- Stop category/behavior as defined by the applicable system standard.
- Worst-case stop time/distance and protective-distance owner.
- Brake/holding proof tests, inspection and replacement interval.
- Hard-stop energy and post-event inspection criteria.
- Fault-injection results and diagnostic coverage source.
- Residual-risk decision by a named authorized human.

ISO 9283:1998 supplies performance criteria and test methods for manipulating industrial robots; it is not a safety certification. Define repeat count, warm-up, load, speed, pose set, environment, measurement uncertainty and statistical treatment for every claimed performance result.
