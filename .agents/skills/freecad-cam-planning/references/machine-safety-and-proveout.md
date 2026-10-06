# Machine safety and prove-out

This reference defines a handoff boundary, not an operating procedure. Follow the machine manufacturer, site safety program, controller manual, risk assessment, and authorized machinist.

## Before posting

- Confirm machine/controller/post combination and post revision.
- Confirm stock, fixture, clamps, jaws, tool assemblies, work envelope, and operation order.
- Verify model and drawing revision/checksum.
- Verify WCS and setup orientation.
- Ensure all toolpaths pass CAM sanity, inspection, and simulation.

## Posted-code review

Controller-specific review should cover:

- Program number/name and revision.
- Units, absolute/incremental mode, plane, arc-center convention, and feed mode.
- Work coordinate, local shifts/rotation/scaling/mirroring, and cancellation.
- Tool selection/change, length and radius compensation, and offsets.
- Spindle direction/speed, CSS limits where applicable, coolant, and dwell.
- Canned cycles and their cancel state.
- Safe retracts and machine-coordinate moves.
- Rapids near stock/fixtures and after tool changes.
- Optional/mandatory stops, probing behavior, subprograms/macros, and restart points.
- Program end and safe machine state.

Do not assume an unfamiliar code is harmless. Resolve it using the exact controller manual.

## Prove-out record

The authorized shop defines the sequence. Capture:

- External posted-code backplot/simulation result and machine model version.
- Control graphics result.
- Tool/holder/offset verification.
- Stock and fixture inspection.
- Work-offset establishment and independent check.
- Dry-run/single-block/override settings used.
- Observed clearance and any edited blocks.
- First-piece serial/lot and inspection result.
- Final program checksum and approver.

Any on-control edit must be reconciled back to the controlled CAM/post source or formally documented. Do not let the machine copy become an untracked fork.

## Stop conditions

Stop and escalate on:

- Revision/checksum mismatch.
- Unknown post, code, offset, coordinate system, or unit.
- Unmodeled workholding or insufficient clearance.
- Tool assembly mismatch.
- Feed/speed outside approved limits.
- Unexpected motion in backplot, dry run, or single block.
- First-piece nonconformance.

Source example for machine-specific offsets and cautions: [Haas mill part setup](https://www.haascnc.com/service/online-operator-s-manuals/mill-operator-s-manual/mill---part-setup.html). Always use the actual machine’s manual.
