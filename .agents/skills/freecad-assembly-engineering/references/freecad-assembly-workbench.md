# FreeCAD 1.1.x native Assembly workbench

FreeCAD 1.0 introduced the built-in Assembly workbench; 1.1 added simulation/animation improvements. The 1.1.2 maintenance release is the suite baseline:

- <https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.2>
- <https://blog.freecad.org/2026/03/25/freecad-version-1-1-released/>
- <https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_Workbench.md>

## Architecture

- Create one controlled root product assembly per assembly document.
- Insert linked FCStd component definitions; normalize vendor STEP into a verified FCStd wrapper first.
- Native subassemblies may be rigid or flexible. A rigid subassembly acts as one body at its parent. A flexible one exposes internal joints and must be verified at both levels.
- Use a deliberate grounded base. A missing ground fails solve; extra grounds can create or hide constraint problems.
- Native joint types include fixed, revolute, cylindrical, slider, ball, distance, parallel, perpendicular, angle, rack-and-pinion, screw, gears, and belt.

Official command references:

- Insert Component: <https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_InsertLink.md>
- Assembly creation: <https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateAssembly.md>
- Exploded views: <https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateView.md>
- BOM: <https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateBom.md>
- Simulation: <https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateSimulation.md>

## Production limits

- Solver return success and displayed DOF are necessary checks, not proof of fit or load path.
- STEP hierarchy does not carry FreeCAD joint, motion, or exploded-view semantics.
- Native BOM grouping is not a controlled part-number/revision reconciliation.
- Exploded view authoring and TechDraw review remain GUI-heavy and require rendered visual QA.
- Simulation produces kinematic frames; it is not realistic dynamics.
- Native Assembly does not provide a documented release-grade clash/clearance or tolerance-stack workflow. Use explicit B-rep intersection/distance tests and engineering stacks.
- Joint limits may not be enforced in all simulation contexts; verify end stops independently.

For headless checks, pin the FreeCAD version and integration-test against the project’s object model. Do not claim complete GUI-equivalent diagnostics from a public Python return code alone.
