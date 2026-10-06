# ECAD, boards, servos, and actuators

## PCB and controller boards

Use the exact project/revision/variant whenever possible.

- KiCad can export an assembled PCB STEP model from the command line or PCB editor: <https://docs.kicad.org/9.0/en/cli/cli.html> and <https://docs.kicad.org/master/en/pcbnew/pcbnew.html>
- KiCad StepUp integrates board outline/model placement with FreeCAD: <https://github.com/easyw/kicadStepUpMod/>
- KiCad library terms are CC-BY-SA 4.0 with a design-output exception; collections still have attribution/share-alike obligations: <https://www.kicad.org/libraries/license/>
- Raspberry Pi publishes board-specific mechanical resources, including STEP for some products: <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html> and <https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html>

Record board ID, hardware revision, assembly variant/DNP set, ECAD commit/hash, export tool/version/options, board-to-MCAD transform, and all absent 3D models. A Raspberry Pi or Arduino family name is not enough; board revisions and connector layouts change.

Retain:

- Board outline, thickness, cutouts, holes, slots, and mounting datum.
- Connector mating faces/axes and insertion/removal envelopes.
- Components that are tall, hot, heavy, conductive, user-accessed, or clearance-critical.
- Heat sink, airflow, antenna, high-voltage, optical, test, and programming keepouts.
- Cable exit, strain relief, minimum bend, and service loops.
- Reference designators where assembly/service documentation needs them.

Keep copper/net/fabrication authority in ECAD. STEP is only a mechanical representation.

## Servos and actuators

“Standard-size,” “micro,” and “9 g” are market categories, not reliable mechanical standards. Use an exact manufacturer part number and variant.

- ROBOTIS publishes exact-model STEP/DWG/PDF resources: <https://emanual.robotis.com/docs/en/dxl/mx/mx-64-2/>
- Pololu warns that even “standard-size” servos vary and provides model-specific drawings/CAD: <https://www.pololu.com/product-info-merged/3435>

Capture:

- Housing and mounting ears/holes with tolerance evidence.
- Output-axis datum, spline/tooth specification or shaft/key, and horn/coupler.
- Commanded range, mechanical stops, overtravel risk, and swept volume.
- Cable exit, connector, bend/service envelope, and installation/removal path.
- Tool access and fastener engagement depth.
- Mass, center of gravity, and inertia with provenance.

Never scale a similar servo or assume horn/spline compatibility from body size.
