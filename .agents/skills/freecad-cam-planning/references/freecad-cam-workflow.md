# FreeCAD 1.1 CAM workflow

## Job architecture

A CAM Job contains model clone(s), stock, tool controllers, operations/dressups, setup/output configuration, and ordered workplan. FreeCAD stores an internal machine-agnostic G-code representation; the postprocessor translates it to a controller dialect.

FreeCAD 1.1 replaced the CAM tool-management workflow with an integrated newer tool library/editor. Revalidate legacy `.fctb`, `.fctl`, templates, and scripts.

## Units

- FreeCAD base length/time units are mm and s, so internal velocity is mm/s.
- The displayed unit schema changes input/display behavior, not the posted program’s units.
- The postprocessor owns final `G20`/`G21` output.
- Use the Metric Small Parts & CNC schema for metric CAM input where appropriate and always include explicit unit strings.
- Inspecting internal CAM code may show mm/s even when the post will output mm/min.

## Current limitations

- Most operations are 2.5D; 3D Pocket and 3D Surface provide true 3D paths, with experimental/version-sensitive areas.
- Capability varies by operation/tool shape.
- Clamp and fixture awareness is not automatic.
- CAM scripting documentation can include legacy APIs; verify code against 1.1 source/runtime.
- Simulation does not prove controller semantics, machine kinematics, offsets, or physical setup.

## Setup

1. Audit the final B-rep.
2. Create a Job from the final production solid.
3. Define stock from actual saw/bar/blank dimensions.
4. Transform the model into the real setup orientation.
5. Establish the origin/WCS and document touch-off/probe method.
6. Add controlled tools and ToolControllers.
7. Set feeds/speeds with units.
8. Model workholding separately and maintain clearance.

For multiple physical orientations, create separate Jobs such as
`JOB_A_G54_TOP` and `JOB_B_G55_FLIP`. In each Job:

1. Clone/transform the controlled model into that setup orientation.
2. Define setup-specific incoming stock, including material already removed in a prior setup when this affects clearance or support.
3. Show only the matching fixture/jaw/clamp arrangement.
4. define the setup WCS and zero-establishment method.
5. Add only operations executed before the next unclamp/reorientation.
6. Simulate and post to a distinct program file.

Capture the relationship between the design datum frame and every setup WCS.
Do not rely on a view transform as a manufacturing setup definition.

## Operations

Available operation families include facing, profile, pocket, adaptive, slot, helix, drilling, thread milling, engraving, deburr, 3D pocket/surface, and version-dependent experimental tools.

For every operation check:

- Base geometry and side selection.
- Tool and compensation.
- Heights/depths relative to stock and WCS.
- Stepdown/stepover and stock to leave.
- Entry, ramp, plunge, lead-in/out, and direction.
- Boundary, keep-out, and dressup behavior.
- Linking and rapids.

## Verification and post

1. Run Sanity Check.
2. Inspect toolpath.
3. Simulate material removal.
4. Verify operation order.
5. Post with the Job’s Post Process command.
6. Inspect the posted program and simulate/backplot it in a controller-aware system.

Do not use File → Export for G-code; FreeCAD documentation warns it can produce damaged output.

Sources: [CAM Workbench](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/CAM_Workbench.html), [CAM Post](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/CAM_Post.html), [CAM scripting](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/CAM_scripting.html), and [FreeCAD 1.1 release notes](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Release_notes_1.1.html).
