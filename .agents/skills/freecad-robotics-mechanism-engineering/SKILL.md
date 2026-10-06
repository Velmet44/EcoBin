---
name: freecad-robotics-mechanism-engineering
description: Engineer and verify production robotic mechanisms in and around FreeCAD. Use whenever a task involves robot arms, mobile manipulators, grippers, pan-tilt units, servo linkages, actuators, gearboxes, belts, chains, screws, bearings, kinematics, singularities, workspace, trajectory loads, reflected inertia, torque or thermal sizing, backlash, compliance, accuracy, calibration, brakes, gravity-drop prevention, cable carriers, sensors, URDF/ROS frames, or robot mechanism verification—even when the user only asks whether a robot CAD assembly “will work.”
---

# FreeCAD Robotics Mechanism Engineering

Runtime compatibility: Codex and Claude Code; Python 3.10+ for deterministic contract checks and FreeCAD 1.1.2 or the project-pinned version for geometry and assembly verification.

Engineer the mechanism from required task motion and credible duty cycles back to geometry, drives, structure, controls interfaces, and evidence. A nominal FreeCAD motion animation is not kinematic coverage, dynamic sizing, bearing life, thermal acceptance, positioning performance, or safety validation.

Use `../freecad-assembly-engineering/SKILL.md` for product structure, joints, fits, collision, service access, and assembly release. Use `../freecad-component-sourcing/SKILL.md` for exact servos, motors, gearboxes, brakes, encoders, bearings, and supplier models. Use `../freecad-robot-motion-dynamics-and-validation/SKILL.md` when release-driving inertial, flexible-body, contact, actuator, or control response must be simulated and correlated. Use the CAE and reliability skills when structural, thermal, fatigue, or failure-risk evidence is required.

Read:

- `references/robotics-calculations.md` for kinematic, drive, transmission, bearing, braking, and thermal calculation expectations.
- `references/frames-urdf-and-calibration.md` for coordinate frames, URDF/ROS export, accuracy, and calibration.
- `references/safety-and-verification.md` for hazards, verification, and physical test boundaries.

Copy `assets/robot-mechanism-contract.json` and `assets/robot-verification-matrix.csv` into the project. Run `scripts/robot_mechanism_validate.py` before any production-candidate verdict. The validator checks record consistency and selected arithmetic; it cannot prove geometry, source data, dynamics, safety, or physical performance. `DRAFT` and `CONDITIONAL` are explicitly non-production verdicts.

## Gate 1 — Freeze mission, architecture, and acceptance

Record:

- Product number, revision, released configuration, units, base/world/tool coordinate conventions, owner, maturity, and governing requirements.
- Payload mass, CoG and inertia envelopes; tool and workpiece variants; reach/workspace; speed, acceleration, jerk, accuracy, repeatability, settling, duty cycle, life, environment, contamination, ingress, noise, and service requirements.
- Normal operation, setup, teaching, recovery, maintenance, transport, power loss, foreseeable misuse, human access, and safety consequences.
- Acceptance authority and traceable evidence for each requirement. Separate estimates, simulations, supplier data, and measured results.

Define system boundaries. Distinguish the robot mechanism, end effector, controller, power conversion, cell/application, guarding, fixtures, and payload. Do not silently apply an industrial-robot standard to service, medical, consumer, or mobile systems outside its scope.

## Gate 2 — Build the mechanism and frame architecture

Create a controlled chain/tree of links and joints:

- Give every link, joint, interface, actuator, transmission, bearing, sensor, cable, stop, and frame a stable ID.
- Define base, joint, link, flange, tool, payload, calibration, world, fixture, and sensor frames with handedness, axis directions, origin, and parent.
- Locate joint axes on controlled datums, not transient topology. Record positive motion, home, soft limits, hard limits, useful travel, and stop compliance.
- State which components move together and where compliance, backlash, friction, or lost motion enters.
- Keep visual geometry, collision envelopes, inertial models, and manufacturing definitions traceable but purpose-specific.

For parallel, closed-chain, differential, tendon, cable, or remote-center mechanisms, state loop-closure equations and solver branch selection. A serial-chain assumption is not acceptable by default.

## Gate 3 — Prove kinematics, workspace, and singularity behavior

Derive or verify forward kinematics and, where required, inverse kinematics. Document:

- Coordinate convention, transform order, joint-zero definition, branch selection, numerical tolerance, and validation poses.
- Reachable, dexterous, and collision-free workspace under all tool/payload/configuration variants.
- Jacobian definition and singularity/near-singularity metric with an engineering threshold.
- Joint velocity/acceleration amplification, branch transitions, unreachable commands, limit avoidance, and recovery behavior.
- Critical poses: full extension, folded, maximum gravity moment, wrist alignment, near base, payload pickup/place, and service/recovery positions.

Sampled plots do not prove continuous coverage. Refine around boundaries, extrema, collisions, and singularities; preserve executable calculations and test points.

## Gate 4 — Establish trajectory loads

Size from credible trajectories, not payload mass alone:

1. Define time histories or bounded envelopes for joint position, velocity, acceleration, jerk, dwell, reversal, emergency/controlled stop, and external process forces.
2. Include moving-link mass/inertia, payload/tool uncertainty, gravity orientation, transmission efficiency in both directions, friction, preload, cable forces, shock/impact, imbalance, and simultaneous-axis effects.
3. Calculate torque/force and speed at every joint across the trajectory. Preserve positive/negative power and regenerative/braking cases.
4. Identify peak, RMS/equivalent, continuous, stall/holding, and emergency values with duration and thermal cycle.
5. Apply explicit design factors and uncertainty margins; do not double-count supplier service factors.

Record the governing pose/event for each maximum. Static torque checks cannot clear acceleration, resonance, stopping, or thermal duty.

When dynamic interaction, simultaneous-axis coupling, compliance, impact, actuator saturation, control delay, or resonance materially affects the result, do not reduce the evidence to an unverified scalar torque. Invoke the robot dynamics skill and reconcile controlled time histories, per-link mass/CoG/inertia, solver sensitivity, governing events, and measured correlation back into this sizing record.

## Gate 5 — Size actuators, transmissions, bearings, and structure

For each axis:

- Match required torque-speed-time points to the exact motor/servo/drive voltage, current, cooling, ambient, controller limits, and derating curve.
- Check peak torque duration, RMS/continuous torque, speed, power, bus/drive current, thermal equilibrium/transient, stall/hold, and repeated starts.
- Reflect load inertia through the actual ratio and efficiency; compare motor/load inertia ratio to a justified control-performance target, not a universal folklore limit.
- Check gearbox/transmission input and output ratings, ratio, bidirectional efficiency, backlash, torsional/linear stiffness, lost motion, life, lubrication, preload, shock, reversal, and allowable external loads.
- Check belts/chains/screws/gears/cables for tension, tooth/strand loading, wrap/engagement, critical speed, buckling where applicable, wear, stretch, tensioning and guarding.
- Resolve bearing reaction loads over the duty spectrum. Check static safety, basic/modified rating life where applicable, oscillation, preload, fits, lubrication, contamination, misalignment, thermal expansion, electrical damage, retention, and mounting stiffness.
- Trace structural deflection, joint compliance and natural modes into the endpoint performance budget.

Supplier selection software is evidence, not design authority. Archive input assumptions, exact catalog revision, selection output, and independent boundary checks.

## Gate 6 — Close accuracy, repeatability, backlash, and calibration

Create an endpoint error budget containing geometry tolerances, joint zero, encoder resolution/quantization, gearbox lost motion, bearing clearance, elastic deflection, thermal growth, control following error, fixture/tool/payload uncertainty, and calibration residuals.

Distinguish:

- Accuracy from repeatability.
- Unidirectional from bidirectional behavior.
- Static pose error from path accuracy, overshoot, settling, and drift.
- Nominal model predictions from measured performance.

Define datums, calibration artifacts, measurement system uncertainty, pose set, load/temperature states, algorithm/version, parameter ownership, residual limits, validation data, and recalibration triggers. Never tune away a safety, overload, collision, or hard-stop defect.

## Gate 7 — Engineer stopping and power-loss behavior

For each hazardous axis and pose, create a separate stopping/brake evidence record. Every axis flagged as hazardous must be covered; do not let one axis-level test stand in for the mechanism:

- Define normal, protective, emergency, drive-fault, communication-loss, encoder-fault, overtemperature, and power-loss states.
- Calculate stopping energy/distance/time with credible reaction delay, maximum speed/load, gravity, friction uncertainty, brake build time, transmission compliance, and regenerated energy.
- Verify brake/holding device static and dynamic capacity, duty, wear, release monitoring, diagnostic coverage, and proof-test interval.
- Prevent gravity drop or uncontrolled release where required. Treat a motor holding torque or non-self-locking gearbox as unavailable after power loss unless the architecture proves otherwise.
- Ensure mechanical stops survive the defined event without creating unacceptable rebound, debris, pinch, or hidden damage.

Link safety-related controls to the project’s machinery/robot risk assessment. This skill supports engineering evidence; it does not certify compliance or determine a safety integrity/performance level by itself.

## Gate 8 — Integrate sensors, cables, and controls interfaces

Record encoder/resolver location, transmission path, resolution, accuracy, index/homing, limit switches, brake feedback, torque/force sensing, temperature monitoring, plausibility checks, and fault behavior.

For every cable/hose:

- Define routing, bend/torsion radius, moving length, cycle rating, carrier fill, separation, strain relief, connector retention/keying, grounding/shielding, service loop, pinch/abrasion/heat/chemical exposure, and replaceability.
- Verify swept envelopes across all joints, including compound twist and tool/payload variants.
- Keep electrical limits, communications, firmware/configuration, and connector pinout under revision control.

## Gate 9 — Export URDF/ROS data without corrupting engineering truth

Generate a robot description only from controlled frames and properties:

- One unambiguous parent-child tree, explicit units, right-handed frame convention, joint type/axis/origin/limits, transmissions, and mimic relations where supported.
- Separate collision and visual geometry. Simplify collision meshes deliberately and conservatively; record method, tolerance, and source revision.
- Use positive mass and a physically valid inertia tensor expressed about the stated link frame/CoG. Validate symmetry, principal values, and triangle inequalities.
- Record omitted compliance, friction, backlash, loops, cables, and controller behavior. URDF cannot faithfully encode every real mechanism.
- Round-trip key frames and joint limits between FreeCAD and the robot software stack; run a pose/hash/configuration reconciliation.

Never treat a syntactically valid URDF as proof of correct kinematics or dynamics.

## Gate 10 — Verify and release

Build a requirement-to-evidence matrix covering:

- Geometry, mass/CoG/inertia, limits, stops, fits, backlash, stiffness and free play.
- Kinematics, workspace, singularity thresholds, joint limits, collision/swept volume, cable motion, and tool/payload variants.
- Torque-speed trajectories, peak/RMS/continuous duty, thermal equilibrium, transmission and bearing life, regenerative energy, and braking.
- Accuracy, repeatability, path performance, settling, calibration residuals, drift, and environmental extremes.
- Fault injection, encoder/brake/limit behavior, power loss, protective stop, gravity holding, recovery, maintenance, and inspection.

Require analytical calculation review, independent CAD checks, simulation with verification/convergence as applicable, bench/subassembly tests, and physical system acceptance proportional to consequence. Use current, purchased/licensed standards and applicable regulations; record identifier and edition rather than copying proprietary requirements.

Release the exact FreeCAD and linked-component revisions, contract, frames/joints, calculations, source data, drive selections, load spectra, thermal/structural evidence, URDF/software artifacts, verification results, deviations, residual risks, and human approvals.

A production candidate requires an available physical-verification plan; it does not require a falsely pre-passed built-unit record. Track `planned`, `available`, `in_progress`, `passed`, or `failed` separately. Only `passed` may name executed acceptance evidence and its human acceptance, and released maturity requires that stronger state.

Verdicts:

- `PASS — mechanism production candidate`: all declared engineering gates pass with configuration-specific evidence, including a linked verified dynamics study where the intended claim requires one; remaining manufacturing/system authorization is named.
- `DRAFT`: concept or prototype records are internally consistent but are not production candidates.
- `CONDITIONAL`: exact assumptions, margins, configurations, limitations, and invalidated claims are stated.
- `FAIL`: a blocking architecture, load, sizing, life, thermal, accuracy, stopping, cable, software-interface, or evidence defect exists.
- `RELEASED`: only after authorized approval and required physical acceptance.

Do not claim certification, safety compliance, or physical acceptance from a script, CAD model, simulation, or this skill.
