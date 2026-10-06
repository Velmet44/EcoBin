---
name: freecad-cam-planning
description: Plan, build, review, and document safe, traceable FreeCAD CAM jobs for CNC manufacturing. Use for FreeCAD CAM/Path jobs, stock and work-coordinate setup, tool/holder selection, feeds and speeds, milling or drilling operation sequencing, postprocessor selection, simulation, G-code preflight, setup sheets, collision/workholding review, or controlled machinist handoff. This skill does not authorize running a machine.
---

# FreeCAD CAM Planning

Runtime compatibility: Codex and Claude Code; Python 3.10+ for G-code preflight and FreeCAD 1.1.2 for CAM/Path authoring and simulation.

Use `../freecad-manufacturing-planning-and-material-optimization/SKILL.md` for the upstream production router, stock/yield/nesting decisions, batch economics, and waste accounting. This skill owns CNC setup and toolpath planning for the selected route; CAM cycle estimates alone are not a complete production cost model.

Produce a CAM plan and evidence package for an authorized machinist. Never call posted code machine-ready from FreeCAD simulation alone and never execute CNC equipment.

Target FreeCAD 1.1.2 unless the project pins another version. FreeCAD 1.1 introduced a new CAM tool-library workflow; verify old job templates and scripts before reuse.

Read `references/freecad-cam-workflow.md`, `references/feeds-speeds-and-tooling.md`, and `references/machine-safety-and-proveout.md`.

## Gate 1 — Require a machine contract

Do not post final code until these are identified:

- Machine make/model, axis configuration, travels, rotary convention, spindle limits, tool changer, coolant, probing, and controller.
- Approved controller postprocessor and its revision/configuration.
- Workholding, fixture/clamp/jaw geometry, permitted clamp force, stock, locating scheme, and work coordinate.
- Tool plus holder assemblies with actual diameter, corner/nose radius, flute/cut length, shank/neck, gauge length, stick-out, tool number, and offset convention.
- Material grade/condition, stock state, quantity, required finish/tolerance, and cutting-data source.
- Shop conventions for safety line, optional stops, tool changes, coolant, work offsets, subprograms, arc mode, line length/precision, and program end.

If any item is unknown, create a planning-only CAM job and mark post output `NOT FOR MACHINE USE`.

## Gate 2 — Freeze and audit the manufacturing model

- Use the released or controlled production-candidate revision.
- Run geometry validity/BOP checks before creating CAM.
- Verify units and model orientation.
- Use a dedicated manufacturing model when adding stock allowance, tabs, sacrificial geometry, or setup transformations; do not corrupt nominal design geometry.
- Capture checksum/revision so CAM cannot drift from the drawing.

## Gate 3 — Define job, stock, fixture, and zero

In the FreeCAD CAM Job:

- Select only the intended final solid(s).
- Define real stock size/form and allowance.
- Place the model exactly as clamped.
- Define the job origin to match the intended work offset (for example G54) and document how the operator will establish it.
- Model fixture, jaws, clamps, parallels, stops, chuck, and protected keep-out envelopes.
- Set clearance, safe, retract, start, and final heights from the complete tool/holder/fixture arrangement.

FreeCAD CAM does not automatically account for clamping mechanisms. Visual review without a fixture model is incomplete.

Create one Job per physical setup/orientation. Give each Job its own transformed
model/stock state, fixture visibility, WCS, setup sheet, output filename, and
simulation record. Do not mix a flip/setup change into one ambiguous workplan.

## Gate 4 — Select tools and cutting data

- Use the FreeCAD 1.1 tool-bit library or a controlled shop library.
- Verify geometry against the physical tool and holder; a nominal “6 mm end mill” is insufficient.
- Source surface speed, chip load/feed per revolution, depth/width of cut, coolant, ramp/plunge limits, and tool-life guidance from the tool manufacturer or qualified shop database for the actual material and engagement.
- Calculate RPM/feed with units, then cap/derate for machine, holder, stick-out, rigidity, workholding, entry, and process limits.
- Never copy tutorial feeds/speeds into production.
- Explicitly enter units. FreeCAD stores velocity internally in mm/s; posts commonly output mm/min or in/min.

## Gate 5 — Build the operation plan

Sequence from stable datums and rigidity:

1. Establish/probe work coordinate and verify stock.
2. Face or create reference surfaces as needed.
3. Rough while retaining support and finish stock.
4. Semi-finish/rest-machine where required.
5. Create/finish critical datums and related features in the same setup where practical.
6. Drill/ream/bore/thread using appropriate cycles and chip control.
7. Finish walls/floors/profiles with planned compensation and lead-in/out.
8. Chamfer/deburr where safe.
9. Probe/inspect in process where required.
10. Cut off/release only after support-dependent work.

For each operation verify tool side, direction, compensation, start/final depth, stepdown, stepover, entry, lead, finish allowance, tolerance, coolant, and linking/rapid moves. Review operation order in the Job Workplan.

Use dressups intentionally. Holding tags, dogbones, ramps, boundaries, and lead-in/out alter paths and require re-simulation.

## Gate 6 — Verify before post

- Run CAM Job Sanity Check.
- Inspect the internal toolpath numerically and visually.
- Run FreeCAD CAM Simulator for material removal.
- Confirm no gouge, uncut critical stock, overtravel, invalid rapid, unsafe retract, holder/fixture collision, lost workholding, or tool reach violation.
- Check toolpath extents against stock, machine travel, and rotary limits.
- Review every setup and flipped orientation independently.

FreeCAD’s simulator is idealized and most CAM operations are 2.5D-focused. Use an external simulator/backplot capable of consuming the posted controller code and full machine/holder/fixture model for consequential work.

## Gate 7 — Post and preflight

- Select the exact approved post; do not use File → Export to create G-code.
- Review preamble, units (`G20/G21`), distance mode (`G90/G91`), plane, work offset, tool and length/radius compensation, spindle/coolant, canned cycles, arcs, safe retract, optional stops, and postamble.
- Compare posted coordinates, feeds, speeds, tool numbers, and operation count with the CAM plan.
- Run `scripts/gcode_preflight.py` with a populated, controlled machine profile. An absent, placeholder, or incomplete profile must return `UNCONFIGURED`, never `PASS`. The tool is a lexical/modal screen, not a simulator or certification.
- Populate mode-specific feed limits, explicit `G96/G97` policy, and the machine-coordinate origin of every allowed work offset. Without those transforms the checker cannot compare programmed work coordinates with machine travel and must fail closed.
- Treat `WARN` as a nonzero production result. Use `--allow-warnings` only for a clearly labeled planning-only screen.
- Diff the posted program after any model, tool, CAM, post, or machine-profile change.

## Gate 8 — Authorized shop prove-out

The responsible machinist must complete the site procedure, normally including posted-code simulation/backplot, control preview, offset verification, dry run/graphics, single block, reduced rapid/feed override, safe clearance, first-piece cut, and inspection. Quarantine production quantity until first-piece acceptance.

## Deliverables

Copy `assets/cam-setup-sheet.md` and provide:

- Controlled FreeCAD model and CAM Job.
- Stock/fixture/workholding model and setup images.
- Tool/holder list and cutting-data calculations with sources.
- Operation sheet with setup, WCS, depths, allowances, and inspection points.
- Postprocessor name/revision/options and machine profile.
- Posted program labeled by approval state.
- FreeCAD simulation, external posted-code verification, preflight, prove-out, and first-piece records.

End with `PLANNING ONLY`, `CONDITIONAL FOR PROVE-OUT`, or `SHOP-APPROVED`, naming the approving person/system for the last state.
