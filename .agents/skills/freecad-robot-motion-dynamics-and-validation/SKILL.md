---
name: freecad-robot-motion-dynamics-and-validation
description: Build and validate force-driven multibody, flexible-body, contact, actuator, and controls models for FreeCAD robotic mechanisms. Use for accurate robot physics, dynamic simulation, MBDyn or Project Chrono handoff, mass/CoG/inertia validation, trajectory loads, impact, friction, compliance, vibration, controller co-simulation, solver time-step convergence, FEA load extraction, or correlation between CAD, simulation, and physical robot tests.
---

# FreeCAD Robot Motion Dynamics and Validation

Runtime compatibility: Codex and Claude Code; Python 3.10+ for contract checks; the chosen dynamics solver, control stack, and FreeCAD 1.1.2 or project-pinned versions must be independently installed and pinned.

Create a credible path to accurate physics; never promise automatic accuracy. FreeCAD Assembly Create Simulation uses prescribed joint motion for kinematic visualization. It does not solve force/torque-driven multibody dynamics, contact, actuator saturation, or control response.

Use `../freecad-robotics-mechanism-engineering/SKILL.md` for architecture, kinematics, drives, brakes and performance requirements; `../freecad-assembly-engineering/SKILL.md` for controlled occurrences/joints and clearance evidence; and `../freecad-engineering-analysis-and-optimization/SKILL.md` for stress, thermal, vibration, fatigue and flexible-body substantiation.

Read:

- `references/solver-selection-and-model-boundary.md`
- `references/multibody-controls-and-contact.md`
- `references/dynamics-verification-and-correlation.md`

Copy `assets/motion-dynamics-contract.json`, `assets/link-mass-properties.csv`, `assets/trajectory-schema.csv`, and `assets/dynamics-verification-matrix.csv`. Run `scripts/motion_dynamics_validate.py`.

## Gate 1 — Define the prediction and acceptance claim

State the quantities of interest, configurations, trajectories/events, environments, accuracy limits, consequences, acceptance authority, and what the model will not predict. Separate:

- Prescribed kinematic poses and workspace.
- Rigid/flexible multibody response.
- Local stress/thermal/fatigue response.
- Control and drive behavior.
- Collision geometry from compliant contact/impact.
- Simulation evidence from physical acceptance.

## Gate 2 — Reconcile CAD and physical properties

For every moving link record source revision/hash, material/density source, mass, CoG, inertia tensor, expression frame and point, uncertainty, and measured reconciliation. Check tensor symmetry, positive principal moments, triangle inequalities, units, parallel-axis transforms, payload/tool variants, cables and fluid/consumable states.

Define joints, constraints, branches/loops, backlash, compliance, damping, friction, bearings, transmission inertias, base/fixture compliance, stops, contacts and gravity. A syntactically valid URDF or CAD mass property is not sufficient.

## Gate 3 — Model actuators and controls at the needed fidelity

Record torque-speed/current/voltage limits, drive saturation, gear efficiency in both directions, brake logic, motor electrical/thermal behavior, sample rates, delays, filters, quantization, sensors, controller revision and fault states.

For co-simulation define exchanged variables, frames, units, signs, rates, interpolation/extrapolation, latency, coupling mode, convergence/iteration policy, initialization and failure handling. Validate each subsystem independently before coupling.

## Gate 4 — Select and freeze the solver route

Use FreeCAD for controlled geometry, joints, poses and visualization. Use an independently verified dynamics solver such as MBDyn, Project Chrono, or an approved commercial tool when force-driven response is required. CalculiX/Elmer serve different FEA/multiphysics roles and are not substitutes for a robot controls/MBD model.

Pin solver/version, integrator, step size/adaptation, tolerances, contact formulation, regularization, damping, initial conditions, input hashes, seeds, platform and run script. Qualify any CAD-to-solver exporter with known poses, mass properties, frames, joint limits and round-trip checks.

## Gate 5 — Verify numerics and physics

Require, as applicable:

- Analytical/free-body and simple benchmark comparisons.
- Constraint residuals; reaction and force/moment balance.
- Energy/momentum accounting with explained actuator, damping, friction and impact work.
- Time-step/integrator/tolerance sensitivity for every release-driving quantity.
- Contact penetration, impulse and stiffness/damping sensitivity.
- Closed-loop branch/constraint consistency.
- Flexible-body modal basis/range/participation and reduction sensitivity.
- Parameter uncertainty/sensitivity for friction, damping, backlash, payload, stiffness, delays and contact.
- Deterministic rerun or statistical repeatability for stochastic models.

Animation smoothness and solver completion are not verification.

## Gate 6 — Extract and reconcile engineering loads

For each governing event report joint torque/speed/power, motor/drive current and voltage, bearing/interface reactions, stop/contact impulse, base loads, link acceleration, endpoint error and settling, plus the time/pose/configuration where each occurs. Transfer loads to structural/thermal/fatigue analyses with frame, sign, units, interpolation and conservatism recorded.

Reconcile the dynamic model back to the drive/bearing/brake sizing contract. Do not size from a single scalar peak stripped of duration, direction or simultaneous-axis context.

## Gate 7 — Correlate to physical behavior

Define instrumentation, calibration, bandwidth/sample rate, uncertainty, fixtures, payloads, excitation/trajectory, safe test envelope, measured quantities and acceptance metrics. Correlate time histories, frequencies/modes, loads, currents, positions, temperatures and impacts as applicable.

Separate calibration parameters from validation data. Record discrepancies and model-form uncertainty; do not tune away an unsafe mechanism or use the same data as both calibration and independent validation.

## Gate 8 — Verdict and release

- `PASS — dynamics model credible for declared use`: configuration-specific inputs, numerics, benchmarks, sensitivity, load reconciliation and required physical correlation pass.
- `DRAFT`: exploratory model only.
- `CONDITIONAL`: declared bounded uses remain pending.
- `FAIL`: model/input/numerical/correlation defect invalidates the intended claim.

Release contract, mass properties, trajectories, solver decks/scripts, co-simulation interface, raw and processed results, verification/correlation report, hashes, limitations and approvals. This skill does not certify robot safety or guarantee physical behavior.
