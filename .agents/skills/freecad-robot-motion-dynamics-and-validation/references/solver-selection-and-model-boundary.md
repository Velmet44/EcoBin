# Solver selection and model boundary

FreeCAD 1.1 Assembly Create Simulation defines prescribed linear/angular motion as a function of time and generates animation frames. Its motion definition does not include force, mass, inertia, friction, contact, actuator or control inputs; treat it as kinematic visualization.

MBDyn is an open-source nonlinear multibody/multiphysics solver supporting rigid/flexible bodies, constraints, controls and co-simulation. Project Chrono supports multibody dynamics, contact, FEA, robotics and co-simulation. Both require a controlled, verified mapping from FreeCAD; neither add-on/tool is an automatic extension of FreeCAD engineering truth.

CalculiX and Elmer are appropriate for their supported mechanical/thermal/multiphysics analysis domains. Select from the quantity of interest and required physics, not convenience.

Primary references:

- https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateSimulation.md
- https://www.mbdyn.org/
- https://www.mbdyn.org/Documentation/FAQ.html
- https://github.com/projectchrono/chrono
- https://api.projectchrono.org/
- https://blog.freecad.org/2025/09/16/getting-started-with-fem/
