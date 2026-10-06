# FreeCAD FEM and solver planning

Use this reference when choosing a solver, creating the analysis model, or handing work to an external solver.

## Capability decision

| Need | Candidate route | Required confirmation |
|---|---|---|
| Linear/nonlinear structural and thermomechanical | FreeCAD FEM with CalculiX | Required element, material, contact, load, step, output, and convergence control are supported by the installed versions |
| Thermal, flow, electromagnetic, or coupled equations | FreeCAD FEM with Elmer | Required equations and coupling are exposed and verified |
| Unsupported formulation or qualification workflow | Controlled external solver | Geometry/mesh/deck translation, solver/version, options, hashes, result mapping, and independent benchmark |

FreeCAD’s project documentation describes CalculiX as its principal mechanical/thermomechanical solver and Elmer as suited to thermal, electromagnetic, flow, and coupled work. Feature support evolves, so confirm the installed FreeCAD and solver versions instead of assuming parity with either solver’s full input language.

## Native workflow

1. Freeze a copy or linked analysis configuration; record the source document/revision and geometry checksum.
2. Suppress detail only through named analysis parameters or a reproducible derivation.
3. Check topology, watertight regions, shared interfaces, material regions, thicknesses, beam sections, and units.
4. Create a named FEM analysis container and solver object.
5. Add materials with controlled sources and temperature/direction dependence where needed.
6. Add constraints, loads, contacts, initial conditions, and equations against stable named geometry. Recheck references after recompute.
7. Mesh with Gmsh/Netgen or a controlled external mesher; archive mesher version, settings, quality metrics, and mesh.
8. Write/archive the solver input before execution. Preserve edits made outside FreeCAD as controlled patches or generation scripts.
9. Preserve solver stdout/stderr, warnings, convergence history, raw results, and extraction scripts.
10. Extract quantities at named physical regions or paths, not transient node/element numbers.

FreeCAD 1.1 documentation notes current limitations including mixed/multiple meshes, multistep analyses, some solver features, and unit/post-processing issues. Treat these as version-specific screening points and use an external controlled route when they affect validity.

## External solver handoff

The handoff record should contain:

- Source FCStd/STEP/BREP checksum and export settings.
- Coordinate and unit transforms.
- Named-set mapping for regions, loads, supports, contacts, and probes.
- Mesh/deck generator and exact versions.
- Original generated deck, reviewed patch, and final executed deck.
- Solver executable/version/platform and option files.
- Job command, run logs, restart/state files, raw output, and checksums.
- Result-field mapping, averaging/extrapolation conventions, and extraction script.
- Benchmark that exercises the transferred feature or formulation.

Round-trip a simple known case before trusting a new translator or solver interface.

## Primary sources

- FreeCAD Project Association, “Getting started with FEM” (2025): https://blog.freecad.org/2025/09/16/getting-started-with-fem/
- FreeCAD Project Association, “What’s new in FEM for FreeCAD 1.1?” (2025): https://blog.freecad.org/2025/09/09/what-is-new-in-fem-for-freecad-1-1/
- CalculiX project documentation: https://www.calculix.de/
- Elmer FEM project documentation: https://www.elmerfem.org/blog/documentation/

Verify current versions and controlling organizational procedures before use.
