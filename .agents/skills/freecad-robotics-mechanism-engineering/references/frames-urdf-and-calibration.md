# Frames, URDF/ROS and calibration

## Frame register

For every frame record ID, parent, physical datum, origin, orientation representation, units, axis convention, owning definition/revision and calibration status. Declare whether it is design-nominal, as-built measured, calibrated or runtime-estimated.

ROS REP 103 defines standard units and coordinate conventions; ROS REP 105 defines common mobile-platform frames. Apply them only when relevant and record project exceptions. A frame-name convention does not validate a transform.

## Robot description release

Treat URDF, meshes, controller configuration and calibration parameters as configuration-controlled software artifacts linked to the exact mechanical revision.

Check:

- Unique links/joints and one valid parent for every non-root link.
- Joint origin, axis, type, limits, velocity and effort.
- Mass, CoG and inertia in the declared inertial frame.
- Visual/collision mesh scale, handedness, origin and source hash.
- Conservative collision simplification and excluded details.
- Transmission, mimic, dynamics and controller parameters where supported.
- Closed-loop, parallel, flexible and cable effects that URDF omits.

Run known-pose comparisons against FreeCAD and the physical system. Compare transforms numerically, not visually.

## Inertia sanity

Require positive mass and a symmetric inertia tensor. Principal moments must be positive and satisfy rigid-body triangle inequalities within numerical tolerance. Confirm the tensor is expressed about the stated point and axes; apply the parallel-axis theorem when moving it.

## Calibration plan

Define the observable parameters, reference artifact, measurement system uncertainty, sampled pose/load/temperature space, optimization method, held-out validation set and residual limits. Protect against overfitting by separating calibration and acceptance datasets.

Store:

- Raw observations and environmental conditions.
- Algorithm/source version and random seed where applicable.
- Before/after parameter sets and covariance or uncertainty.
- Residual distributions, outliers and exclusion rationale.
- Configuration applicability and recalibration triggers.

Calibration cannot rescue inadequate stiffness, backlash, sensor resolution, thermal stability or inaccessible workspace. Correct physical defects before compensating them in software.

Official references to consult include ROS REP 103, ROS REP 105 and the ROS 2 URDF documentation. Pin the ROS distribution and package versions used for release.
