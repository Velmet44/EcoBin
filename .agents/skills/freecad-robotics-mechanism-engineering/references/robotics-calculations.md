# Robotics calculation expectations

Use equations as transparent checks, not as substitutes for a validated multibody, structural, thermal, controls, or physical model. State units, sign convention, coordinate frame, source revision, assumptions, uncertainty and governing event.

## Kinematics and trajectories

- Preserve the forward transform chain and independently verify known poses.
- State the inverse-kinematics branch, convergence tolerance and handling of unreachable poses.
- Evaluate a declared Jacobian metric across the useful workspace. Check velocity/torque amplification near singularities.
- Generate position, velocity, acceleration and jerk histories from the actual motion law and controller constraints.

## Drive quantities

For a rotary axis, calculate joint torque from gravity, inertia, external loads, friction, imbalance, cable forces and transmission losses. Evaluate both motion directions because gravity and efficiency are not generally symmetric.

For samples with torque `T_i` held for time `dt_i`, a common thermal-duty measure is:

`T_rms = sqrt(sum(T_i^2 * dt_i) / sum(dt_i))`

Use the motor/vendor’s actual thermal model and allowable duty definition when it differs. Include dwell and holding states. Peak torque is checked separately against duration, speed, voltage/current and drive limits.

For reduction ratio `N = motor_speed / load_speed`, the ideal load inertia reflected to the motor is:

`J_ref = J_load / N^2`

Add rotor-side couplings, gearbox input inertia and other elements at their correct speed ratio. Efficiency affects torque/power but not this ideal kinematic inertia transform. Justify the permissible reflected-load-to-motor-inertia ratio from bandwidth, compliance, tuning and disturbance requirements.

## Transmissions and bearings

- Check the exact gearbox, belt, chain, screw, gear or cable-drive rating method and supplier load spectrum.
- Include torque reversal, emergency events, overhung/radial/axial loads, misalignment, backlash, stiffness, life, lubrication and contamination.
- Bearing basic rating life may be evaluated under ISO 281 where applicable, but its scope does not cover every wear, corrosion, electrical-erosion, oscillation or contamination mechanism. Use the current controlled standard and bearing manufacturer method.
- Verify shaft, hub, key/spline, fastener and housing interfaces; a rated gearbox output torque does not automatically approve its mounting or external loads.

## Braking and thermal behavior

At minimum, calculate kinetic, gravitational and elastic energy for the governing stop:

`E_stop = delta_kinetic_energy + adverse_delta_potential_energy + released_elastic_energy`

Then include drive reaction delay, regenerative capacity, resistor/bus limits, friction uncertainty, brake build time, repeated-stop duty and transmission compliance. A static brake holding rating does not establish dynamic stopping capacity.

Use a thermal network or validated supplier method with motor copper/iron loss, drive loss, gearbox loss, brake heat, ambient, enclosure, airflow and duty. Check steady and transient temperatures at sensors and inaccessible hot spots.

## Performance evidence

Record:

- Requirement, calculation ID/version and source dataset hash.
- Governing configuration, payload, pose, motion and environment.
- Nominal result, uncertainty/margin, allowable limit and pass/fail.
- Independent review and correlation to bench or system test where consequence warrants it.

Primary standards to evaluate for applicability include ISO 9283:1998 for industrial-robot performance test methods and ISO 281:2007 for rolling-bearing rating life. Confirm current status and obtain the controlled text before use.
