# Revision, inspection, and release control

## Characteristic-to-evidence matrix

For every CTQ record:

| CTQ | Requirement/source | CAD parameter/feature | Process/setup | Inspection/datum simulation | Evidence | Result |
|---|---|---|---|---|---|---|

The matrix must resolve from requirement to model to manufacturing to measurement. Missing links block a production claim.

## Inspection planning

Confirm:

- The datum reference frame can be physically simulated.
- The measurement system has suitable range, resolution, access, fixturing, and uncertainty.
- Temperature, material condition, coating, and restraint state are specified.
- In-process checks occur before a feature becomes inaccessible or distortion-prone.
- Final inspection occurs after the last operation that can change the CTQ.
- Sampling/first article/100% policy matches risk and quality system.
- Functional gauges represent maximum/minimum material and assembly intent correctly where used.

## Revision impact

Classify every change:

- Geometry/parameter.
- Material/condition.
- Process/supplier/machine/workholding.
- Finish/heat treatment/coating.
- Tolerance/GD&T/datum/inspection.
- CAM/tool/post/code.
- Documentation-only.

Re-run all dependent evidence. A geometry change can invalidate TechDraw attachments, STEP, mesh, DFM, FEA, tolerance stack, CAM, fixture, gauge, and first-article results even if the filename is unchanged.

## Release directory

Use an immutable structure such as:

```text
PARTNO_REV/
  native/
  exchange/
  drawing/
  manufacturing/
  inspection/
  evidence/
  release-manifest.json
```

Avoid relying on folder names alone. Record SHA-256 for every controlled file.

## Handoff

Before transfer:

1. Verify the manifest.
2. Confirm no temporary/stale files.
3. Confirm recipient and intended use.
4. Transfer through the approved system.
5. Capture acknowledgement and supplier exceptions.
6. Quarantine superseded revisions according to the quality system.

## Approval

Record named approvals for design, manufacturing, quality/inspection, and other required functions. `RELEASED` is an organizational state, not a property the CAD automation can self-assign.
