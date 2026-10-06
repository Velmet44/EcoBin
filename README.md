# EcoBin

## CAD build status

FreeCAD native models live in `3D-Design/parts/` (one file per print-register ID), assemblies in `3D-Design/assemblies/`, renders in `media/renders/`. Generator scripts in `scripts/cad/` rebuild every file deterministically through the FreeCAD MCP (`exec(open('scripts/cad/<stage>.py').read())`); re-runs wipe and rebuild only their own documents.

Locked layout (owner decisions): Ø300 × 350 mm envelope, 60 mm / 150 g max item, separate lift-out bins, shared lab printer (210 × 210 × 240 mm target).

- [x] Stage 0 — `00_Master.FCStd`: shared `Params` spreadsheet + skeleton datums (carousel axis, drop axis, 3 datum planes, 4 index points). No printable solids.
- [x] Stage 1 — frame / bearing / motor mount: `PR-001_BaseFrame`, `PR-013_BearingSeat` (Ø70 placeholder bore — bearing pick open), `PR-019_StepperMount` (NEMA-17 31 mm BCD), `PR-012_Hub` (Ø5 shaft bore + M3 set-screw drill).
- [ ] Stage 2 — carrier quadrants, chambers A–D, clips.
- [ ] Stage 3 — tray + trapdoor gate.
- [ ] Stage 4 — sensor/camera/display mounts + trim.
- [ ] Stage 5 — linked `EcoBin_Top` assembly.
- [ ] Stage 6 — print release + spool roll-up.

## Buy the demonstrator BOM

The current itemized bill of materials is [`docs/bom/EcoBin-Demonstrator-BOM.csv`](docs/bom/EcoBin-Demonstrator-BOM.csv). It covers purchased components, make/print parts, software, project files, and tools/access assumptions. **No preassembled electronics/project kits or combined load-cell/HX711 bundles are selected.** Retailers' unavoidable component pack sizes (for example, 10 LEDs or 10 resistors) are called out as packs, not treated as project kits.

### Price snapshot and limitations

Prices and availability below were checked on **2026-10-06**. The displayed-price subtotal for currently priced INR items is **₹3,752**, plus **US$15.99** for the standalone Waveshare camera. The single mains input is the 12 V adapter; the P4 board is header-powered from a second LM2596 buck, so no separate USB-C mains adapter is purchased. The INR subtotal uses the two ElectronicsComp prices before GST; their listed prices are explicitly ex-GST, so 18% GST adds ₹25.92 to those two lines if charged. Robocraze tax treatment, shipping, and all supplier checkout charges are not confirmed. Do not treat these partial subtotals as a landed or final project cost.

The INR subtotal includes one provisional NEMA-17/DRV8825 pair, two LM2596 buck modules (one SERVO rail, one LOGIC rail), and one 1 kg filament spool. The motor current/driver match is not confirmed and the spool may not print all 30 registered parts. The 12 V 5 A adapter is provisionally adequate for driver plus both bucks, subject to measured motor current. The barrel breakout, 12 V distribution block, panel switch, fuse, turntable bearing, shaft coupling, and CAD-dependent fastener quantities are required but remain unpriced. The individual P4 board-only listing was last seen at ₹2,519 but could not be revalidated in this check; it is deliberately excluded from the subtotal. Waveshare's USD listings exclude shipping/import costs.

### Robu

- [ESP32-P4-WIFI6 board-only listing — Robu seller reference R255962](https://robu.in/product/waveshare-esp32-p4-wifi6-dev-kit/) — one controller board; last-observed ₹2,519 is **unverified** because Robu blocked revalidation. Confirm the package is the single board before checkout. Do not buy Waveshare Basic Kit / Kit A / Kit B / Kit C.

### Waveshare

- [RPi Camera (B), OV5647, 5 MP — Waveshare SKU 8193](https://www.waveshare.com/rpi-camera-b.htm) — US$15.99. This is a separate camera order; its listed package includes flex leads. Check the included cable orientation and P4 camera-driver compatibility before purchase. Do not also buy a camera-containing board bundle.

### ElectronicsComp

- [5 kg load cell — standalone](https://www.electronicscomp.com/5kg-load-cell-sensor-india) — ₹108 before GST.
- [HX711 load-cell amplifier — standalone module](https://www.electronicscomp.com/hx711-load-cell-amplifier-module) — ₹36 before GST.

These are two separate order lines; the combined load-cell/HX711 product is not selected.

### Robocraze

- [17HS8401S NEMA-17 stepper motor, 48 mm](https://robocraze.com/products/17hs8401s-nema17-stepper-motor-48mm) — ₹899; verify phase-current rating and motor/driver compatibility before ordering.
- [DRV8825 stepper-driver module](https://robocraze.com/products/drv8825-stepper-motor-driver-module) — ₹115; set current only after confirming the motor datasheet and provide required cooling.
- [MG90S 180° micro servo](https://robocraze.com/products/mg90s-servo-motor) — ₹145; verify linkage torque/travel on the printed trapdoor.
- [Hall-effect sensor module](https://robocraze.com/products/hall-effect-sensor-module) — ₹36; open-collector output. Pull the signal up to 3.3 V, not 5 V, at the P4 GPIO and check the module's contradictory supply-voltage copy before wiring.
- [1.3-inch I²C OLED, 128×64](https://robocraze.com/products/1-3in-oled-display) — ₹339 as shown by the current product variant (the page body also contains stale ₹272 copy); confirm controller IC and checkout price.
- [12 V, 5 A DC adapter](https://robocraze.com/products/kento-g-12v-power-adapter-5a-60w-with-5-5mm-dc-plug-standard-ac-to-dc-power-supply) — ₹429; confirm barrel size/polarity and final motor current.
- [LM2596 adjustable buck module](https://robocraze.com/products/lm2596-dc-dc-buck-module) — ₹48; SERVO rail. Set and meter 5.0 V before connecting the servo; label the module.
- [LM2596 adjustable buck module, second unit](https://robocraze.com/products/lm2596-dc-dc-buck-module) — ₹48; LOGIC rail feeding the P4 header `VCC_5V`/`GND`. Set 5.0 V and meter before connecting; never feed `ESP_3V3` or `VBUS_OUT`. Keep USB-C power disconnected while header-powered.
- [USB-C data cable, 1 m](https://robocraze.com/products/erd-uc-230-usb-type-c-fast-charging-data-cable-1-meter) — ₹74; data-only host connection while running on 12 V. Disconnect the 12 V input before flashing so USB `VBUS` and header `VCC_5V` never drive the rail together.
- [5 mm white LEDs, pack of 10](https://robocraze.com/products/5mm-white-led-pack-of-10) — ₹31; individual emitters, bought in the seller's pack size.
- [220 Ω resistors, pack of 10](https://robocraze.com/products/220-ohm-resistor-pack-of-10) — ₹9; use one current-limiting resistor per LED after checking LED forward voltage/current.
- [4.7 kΩ resistors, pack of 10](https://robocraze.com/products/4-7k-resistor-pack-of-10) — ₹12; one can be used as a 3.3 V Hall-output pull-up if confirmed suitable.
- [Female-to-female jumper leads, 20 cm, pack of 40](https://robocraze.com/products/f2f-jumper-wires-20cm-40pcs) — ₹55; commodity wire pack, not an electronics kit.
- [eSun PLA+, 1.75 mm, 1 kg cold-white spool](https://robocraze.com/products/esun-1-75mm-pla-3d-printing-filament-1kg-cold-white-color) — ₹1,339 for one spool; provisional minimum purchase unit only. Determine total spool count from CAD/slicer output.

### Probots

- [5 × 3 mm neodymium disc magnet](https://probots.co.in/5mm-x-3mm-neodymium-round-magnet.html) — ₹29 including GST; one separate magnet for the Hall home target.
- [M3 × 8 mm screw + nut pair](https://probots.co.in/m3x8mm-bolts-and-nuts.html), [M3 × 10 mm pair](https://probots.co.in/m3x10mm-bolts-and-nuts.html), [M3 × 20 mm pair](https://probots.co.in/m3x20mm-bolts-and-nuts.html), [M3 × 25 mm pair](https://probots.co.in/m3x25mm-bolts-and-nuts.html) — each listing is ₹3 including GST for one screw and one nut. Choose lengths/counts after CAD; no assorted fastener kit is selected.

### Pending exact selection / not in the priced subtotal

The CSV keeps these explicit rather than guessing: 12 V barrel breakout and distribution block, panel power switch and fuse rating (all required for the single-input design), turntable bearing size/type, motor-to-carousel coupling/hub, board/module headers including the `VCC_5V`/`GND` power leads, washers/standoffs, motor extension wiring, optional IR break-beam sensor, and exact fastener quantities. Their fit depends on the packaging layout, selected shaft, and wiring diagram. Pending catalogue links are grouped here: [Probots mechanical accessories](https://probots.co.in/robotics-hardware/mechanical-accessories.html), [Probots shaft couplers](https://probots.co.in/robotics-hardware/shaft-couplers.html), [Probots switches](https://probots.co.in/electronic-components/switches.html), [Probots connectors](https://probots.co.in/tools-connectors/connectors/), and Robocraze [sensor](https://robocraze.com/collections/sensors) and [wire/connector](https://robocraze.com/collections/wires-connectors) categories. These are category links, not approved product SKUs, and have no BOM price until fit is decided. Tools such as a ≥220 × 220 × 250 mm FDM printer, computer, soldering station, multimeter, hand tools, and known-mass calibration objects are listed as assumed-owned/shared or still unpriced; the software links in the CSV are free/open source.
