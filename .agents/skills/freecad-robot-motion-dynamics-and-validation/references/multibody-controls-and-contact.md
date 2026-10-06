# Multibody, controls, and contact

Use the minimum model fidelity that resolves the declared quantity:

- Rigid MBD for gross motion and interface loads when flexibility is negligible.
- Flexible bodies or co-simulation with FEA when modes/deformation affect loads, accuracy or control.
- Compliant contact when impact, grasp, stop, gear mesh, wheel-ground or intermittent constraint loads govern.
- Electrical/drive and controller models when current/voltage limits, saturation, delay, bandwidth or fault logic affect response.

Document friction law, regularization, damping, restitution/contact stiffness, backlash/dead zone, preload and initial contact state. Numerical contact parameters can dominate peaks; show sensitivity and use impulse/filtered metrics appropriate to the physical bandwidth.

For co-simulation define a versioned interface contract. Algebraic loops, inconsistent initialization, sample-and-hold delay, non-passive coupling and unit/frame mistakes can produce plausible but wrong motion.

MBDyn’s official documentation describes nonlinear mechanics plus electric, hydraulic and control coupling and external solver interfaces. Project Chrono documentation describes rigid/flexible multibody, contact and robotics capabilities. Solver capability is not model validation.
