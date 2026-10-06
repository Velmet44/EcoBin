# Feeds, speeds, and tool assembly

## Source hierarchy

Use, in order:

1. Tool manufacturer data for the exact tool family, diameter, grade/coating, material group, operation, and engagement.
2. Qualified shop database or proven program on the same machine/material/setup.
3. Machine/tooling applications engineer.
4. Conservative calculation for planning, explicitly unapproved.

Never use a tutorial, generic web calculator, or another material’s value as production authority.

## Core metric calculations

For a rotating cutter:

```text
n [rev/min] = (1000 × Vc [m/min]) / (π × D [mm])
Vf [mm/min] = fz [mm/tooth] × z [teeth] × n [rev/min]
```

For drilling/turning feed per revolution:

```text
Vf [mm/min] = fn [mm/rev] × n [rev/min]
```

For turning surface speed, use current cutting diameter:

```text
n [rev/min] = (1000 × Vc [m/min]) / (π × D [mm])
```

Cap RPM and feed to machine/tool/holder limits. For CSS turning, define maximum spindle RPM.

## Adjustments

Manufacturer starting data still requires adjustment for:

- Radial and axial engagement, full-slot versus side milling, and toolpath strategy.
- Stick-out, neck reach, holder balance, runout, and tool deflection.
- Machine power/torque, acceleration, rigidity, spindle interface, and coolant delivery.
- Workpiece rigidity, clamping, thin walls, interrupted cuts, scale/hard spots, and residual stress.
- Entry/ramp/plunge capability, chip evacuation, recutting, heat, and material condition.
- Desired finish, tolerance, tool life, and process stability.

Document the chosen percentage/derating and reason.

## Tool assembly

Record:

- Unique tool number and controlled library ID/revision.
- Tool type, manufacturer/order code, substrate/coating, diameter, flute count, corner radius/chamfer, helix.
- Overall, flute/cutting, neck, and shank dimensions.
- Holder/collet/arbor and gauge length.
- Programmed stick-out and verified minimum clearance.
- Maximum RPM, coolant, and balance constraints.
- Offset/compensation strategy and presetter/measuring method.

CAM collision checks must use the assembly, not only the cutting cylinder.

## Finish and tolerance

Plan separate rough and finish passes when needed. Leave deliberate radial/axial stock and account for tool deflection/spring, heat, and material movement. Use a finishing operation/tool/process that can achieve required form and texture; feed marks alone do not define achieved surface texture.

## Approval

Mark every value as `CALCULATED`, `MANUFACTURER START`, `PROVEN`, or `MACHINIST APPROVED`. Only the last two should enter an approved production program under the shop’s quality system.
